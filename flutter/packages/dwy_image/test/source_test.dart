import 'dart:async';
import 'dart:io';
import 'dart:typed_data';

import 'package:dwy_image/dwy_image.dart';
import 'package:flutter/painting.dart';
import 'package:flutter_test/flutter_test.dart';

import 'support.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test(
    'network cache keys isolate accounts even when URL and headers match',
    () async {
      final first = await TestCache.create('source_account_a');
      final second = await TestCache.create('source_account_b');
      addTearDown(first.close);
      addTearDown(second.close);
      final uri = Uri.parse('https://images.example.test/avatar.png');
      final a = DwyImageSource.network(
        uri,
        cache: first.cache,
        headers: const {'Authorization': 'Bearer private'},
      );
      final b = DwyImageSource.network(
        uri,
        cache: second.cache,
        headers: const {'Authorization': 'Bearer private'},
      );
      expect(a.provider(), isNot(b.provider()));
      expect(a.provider(cacheWidth: 40), isNot(b.provider(cacheWidth: 40)));
      expect(a.toString(), isNot(contains('private')));
      expect(a.toString(), isNot(contains(uri.toString())));
    },
  );

  test('rejects unsafe URLs and invalid dimensions before image I/O', () async {
    final cache = await TestCache.create('source_validation');
    addTearDown(cache.close);
    for (final url in [
      'file:///private/photo.png',
      'https://user:password@example.test/a.png',
      'https://images.example.test/a.png#fragment',
      '/relative.png',
    ]) {
      expect(
        () => DwyImageSource.network(Uri.parse(url), cache: cache.cache),
        throwsArgumentError,
      );
    }
    expect(() => DwyImageSource.memory(Uint8List(0)), throwsArgumentError);
    expect(() => DwyImageSource.asset(''), throwsArgumentError);
    expect(() => DwyImageSource.file(' '), throwsArgumentError);
    final source = DwyImageSource.memory(Uint8List.fromList([1]));
    expect(() => source.provider(cacheWidth: 0), throwsArgumentError);
  });

  test('asset, local and memory sources use Flutter providers', () async {
    final source = DwyImageSource.asset('images/icon.png', package: 'demo');
    expect(source.provider(), isA<AssetImage>());
    expect(
      (source.provider() as AssetImage).keyName,
      'packages/demo/images/icon.png',
    );
    expect(
      DwyImageSource.file('/tmp/example.png').provider(),
      isA<FileImage>(),
    );
    expect(
      DwyImageSource.memory(Uint8List.fromList([1])).provider(),
      isA<MemoryImage>(),
    );
    final resized =
        source.provider(cacheWidth: 80, cacheHeight: 60) as ResizeImage;
    expect(resized.width, 80);
    expect(resized.height, 60);
    expect(resized.policy, ResizeImagePolicy.fit);
  });

  test('namespace ownership is exclusive and dispose rejects reuse', () async {
    final cache = await TestCache.create('source_lifecycle');
    expect(
      () => DwyImageCache(namespace: 'source_lifecycle'),
      throwsStateError,
    );
    expect(() => DwyImageCache(namespace: '../unsafe'), throwsArgumentError);
    expect(
      () => DwyImageCache(namespace: 'invalid_limits', maxObjects: 0),
      throwsArgumentError,
    );
    await cache.close();
    expect(
      () => cache.cache.keyFor(Uri.parse('https://example.test/a')),
      throwsStateError,
    );
    final replacement = await TestCache.create('source_lifecycle');
    await replacement.close();
  });

  test(
    'clear waits for an active response and removes its completed file',
    () async {
      await HttpOverrides.runWithHttpOverrides(() async {
        final release = Completer<void>();
        final started = Completer<void>();
        final bytes = await imageBytes();
        final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
        final serving = server.forEach((request) async {
          started.complete();
          await release.future;
          request.response.headers.contentType = ContentType('image', 'png');
          request.response.headers.set('cache-control', 'max-age=3600');
          request.response.add(bytes);
          await request.response.close();
        });
        final cache = await TestCache.create('source_pending_clear');
        try {
          final uri = Uri.parse('http://127.0.0.1:${server.port}/photo.png');
          final reading = cache.cache.manager
              .getFileStream(uri.toString(), key: cache.cache.keyFor(uri))
              .drain<void>();
          await started.future;
          var cleared = false;
          final clearing = cache.cache.clear().then((_) {
            cleared = true;
          });
          await Future<void>.delayed(Duration.zero);
          expect(cleared, isFalse);
          release.complete();
          await reading;
          await clearing;
          expect(
            await cache.cache.manager.getFileFromCache(cache.cache.keyFor(uri)),
            isNull,
          );
        } finally {
          if (!release.isCompleted) release.complete();
          await cache.close();
          await server.close(force: true);
          await serving;
        }
      }, RealHttpOverrides());
    },
  );
}
