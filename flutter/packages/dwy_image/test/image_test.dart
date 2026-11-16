import 'dart:io';
import 'dart:typed_data';

import 'package:dwy_image/dwy_image.dart';
import 'package:material_ui/material_ui.dart';
import 'package:flutter_cache_manager/flutter_cache_manager.dart';
import 'package:flutter_test/flutter_test.dart';

import 'support.dart';

void main() {
  testWidgets('memory images decode to bounds while preserving aspect ratio', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetDevicePixelRatio);
    final bytes = await tester.runAsync(imageBytes);
    await tester.pumpWidget(
      MaterialApp(
        home: Center(
          child: DwyImage(
            source: DwyImageSource.memory(bytes!),
            width: 100,
            height: 100,
            semanticLabel: 'Sample picture',
          ),
        ),
      ),
    );
    await tester.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 50)),
    );
    await tester.pumpAndSettle();
    final image = tester.widget<RawImage>(find.byType(RawImage)).image!;
    expect(image.width / image.height, 2);
    expect(image.width, lessThanOrEqualTo(100));
    expect(tester.getSize(find.byType(DwyImage)), const Size(100, 100));
    expect(find.bySemanticsLabel('Sample picture'), findsOneWidget);
  });

  testWidgets(
    'failed image keeps layout and retry remains usable with large text',
    (tester) async {
      final source = DwyImageSource.memory(Uint8List.fromList([0, 1, 2]));
      await tester.pumpWidget(
        MaterialApp(
          builder: (context, child) => MediaQuery(
            data: MediaQuery.of(context)
                .copyWith(textScaler: const TextScaler.linear(2)),
            child: child!,
          ),
          home: Center(
            child: DwyImage(
              source: source,
              width: 80,
              height: 80,
              retryLabel: 'Retry image',
            ),
          ),
        ),
      );
      await tester.runAsync(
        () => Future<void>.delayed(const Duration(milliseconds: 50)),
      );
      await tester.pumpAndSettle();
      expect(tester.getSize(find.byType(DwyImage)), const Size(80, 80));
      expect(find.text('Retry image'), findsOneWidget);
      await tester.tap(find.text('Retry image'));
      await tester.runAsync(
        () => Future<void>.delayed(const Duration(milliseconds: 50)),
      );
      await tester.pumpAndSettle();
      expect(find.text('Retry image'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'network prefetch caches, invalidation reloads and scope clear is isolated',
    (tester) async {
      await tester.pumpWidget(const MaterialApp(home: SizedBox()));
      final context = tester.element(find.byType(SizedBox));
      await tester.runAsync(
        () => HttpOverrides.runWithHttpOverrides(() async {
          final bytes = await imageBytes();
          var requests = 0;
          final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
          final serving = server.forEach((request) async {
            requests++;
            expect(request.headers.value('x-image-test'), 'present');
            if (requests == 1) {
              request.response.statusCode = 503;
              await request.response.close();
              return;
            }
            request.response.headers.contentType = ContentType('image', 'png');
            request.response.headers.set('cache-control', 'max-age=3600');
            request.response.add(bytes);
            await request.response.close();
          });
          final first = await TestCache.create('widget_account_a');
          final second = await TestCache.create('widget_account_b');
          try {
            final uri = Uri.parse('http://127.0.0.1:${server.port}/photo.png');
            final a = DwyImageSource.network(
              uri,
              cache: first.cache,
              headers: const {'x-image-test': 'present'},
            );
            final b = DwyImageSource.network(
              uri,
              cache: second.cache,
              headers: const {'x-image-test': 'present'},
            );
            await expectLater(
              a.prefetch(context, cacheWidth: 40),
              throwsA(isA<HttpExceptionWithStatus>()),
            );
            await a.invalidate();
            await a.prefetch(context, cacheWidth: 40);
            await a.prefetch(context, cacheWidth: 40);
            expect(requests, 2);
            final key = first.cache.keyFor(uri);
            expect(await first.cache.manager.getFileFromCache(key), isNotNull);
            await a.invalidate();
            await a.prefetch(context, cacheWidth: 40);
            expect(requests, 3);
            await b.prefetch(context, cacheWidth: 40);
            expect(requests, 4);
            await first.cache.clear();
            expect(await first.cache.manager.getFileFromCache(key), isNull);
            expect(
              await second.cache.manager.getFileFromCache(
                second.cache.keyFor(uri),
              ),
              isNotNull,
            );
            await b.prefetch(context, cacheWidth: 40);
            expect(requests, 4);
          } finally {
            await first.close();
            await second.close();
            await server.close(force: true);
            await serving;
          }
        }, RealHttpOverrides()),
      );
      await tester.pump();
    },
  );
}
