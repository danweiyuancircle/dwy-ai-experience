import 'dart:io' as io;
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:dwy_image/dwy_image.dart';
import 'package:file/file.dart' as pf;
import 'package:file/local.dart';
import 'package:flutter_cache_manager/flutter_cache_manager.dart';

Future<Uint8List> imageBytes({int width = 200, int height = 100}) async {
  final recorder = ui.PictureRecorder();
  final canvas = ui.Canvas(recorder);
  canvas.drawRect(
    ui.Rect.fromLTWH(0, 0, width.toDouble(), height.toDouble()),
    ui.Paint()..color = const ui.Color(0xFF2563EB),
  );
  final picture = recorder.endRecording();
  final image = await picture.toImage(width, height);
  try {
    final data = (await image.toByteData(format: ui.ImageByteFormat.png))!;
    return data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
  } finally {
    image.dispose();
    picture.dispose();
  }
}

final class TestCache {
  TestCache._(this.directory, this.cache);
  final io.Directory directory;
  final DwyImageCache cache;

  static Future<TestCache> create(String namespace) async {
    final directory = await io.Directory.systemTemp.createTemp(
      'dwy-image-test-',
    );
    final cache = DwyImageCache.custom(
      namespace: namespace,
      repository: JsonCacheInfoRepository(path: '${directory.path}/index.json'),
      fileSystem: _TestFiles(directory.path),
    );
    return TestCache._(directory, cache);
  }

  Future<void> close() async {
    await cache.dispose();
    await directory.delete(recursive: true);
  }
}

final class _TestFiles implements FileSystem {
  _TestFiles(this.path);
  final String path;
  @override
  Future<pf.File> createFile(String name) async =>
      const LocalFileSystem().directory(path).childFile(name);
}

final class RealHttpOverrides extends io.HttpOverrides {}
