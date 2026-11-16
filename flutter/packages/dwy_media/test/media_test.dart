import 'package:dwy_media/dwy_media.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test(
    'library reads limited assets without requesting broader access',
    () async {
      final adapter = FakeLibrary()..access = DwyMediaAccess.limited;
      final library = DwyPhotoLibrary.withAdapter(adapter);
      final albums = await library.albums(kind: DwyMediaKind.images);
      final page = await library.assets(albums.single, page: 0, size: 2);
      expect(albums.single.count, 3);
      expect(page.items.map((asset) => asset.id), ['0', '1']);
      expect(page.mayHaveMore, isTrue);
      expect(page.nextPage, 1);
      expect(adapter.requestCount, 0);
      expect(adapter.lastKind, DwyMediaKind.images);
      final tail = await library.assets(albums.single, page: 1, size: 2);
      expect(tail.items.map((asset) => asset.id), ['2']);
      expect(tail.nextPage, isNull);
    },
  );

  test('denied library does not enumerate or automatically prompt', () async {
    final adapter = FakeLibrary()..access = DwyMediaAccess.denied;
    final library = DwyPhotoLibrary.withAdapter(adapter);
    await expectLater(
      library.albums(kind: DwyMediaKind.images),
      throwsA(
        isA<DwyMediaException>().having((e) => e.code, 'code', 'access_denied'),
      ),
    );
    expect(adapter.listCount, 0);
    expect(adapter.requestCount, 0);
    expect(
      await library.requestAccess(kind: DwyMediaKind.images),
      DwyMediaAccess.denied,
    );
    expect(adapter.requestCount, 1);
  });

  test(
    'paging and thumbnail bounds reject invalid input before plugin work',
    () async {
      final adapter = FakeLibrary();
      final library = DwyPhotoLibrary.withAdapter(adapter);
      final album = (await library.albums(kind: DwyMediaKind.images)).single;
      await expectLater(library.assets(album, page: -1), throwsArgumentError);
      await expectLater(
        library.assets(album, page: 0, size: 0),
        throwsArgumentError,
      );
      await expectLater(
        library.assets(album, page: 0, size: 201),
        throwsArgumentError,
      );
      await expectLater(
        library.thumbnail(asset(0), width: 0, height: 200),
        throwsArgumentError,
      );
      expect(adapter.pageCount, 0);
      expect(adapter.thumbnailCount, 0);
    },
  );

  test('limited manager rechecks state after the system selection', () async {
    final adapter = FakeLibrary()..access = DwyMediaAccess.limited;
    final library = DwyPhotoLibrary.withAdapter(adapter);
    expect(
      await library.manageLimitedAccess(kind: DwyMediaKind.images),
      DwyMediaAccess.authorized,
    );
    expect(adapter.manageCount, 1);
  });

  test(
    'missing or cloud-unavailable file is an explicit unavailable result',
    () async {
      final library = DwyPhotoLibrary.withAdapter(FakeLibrary());
      await expectLater(
        library.open(asset(0)),
        throwsA(
          isA<DwyMediaException>().having(
            (e) => e.code,
            'code',
            'asset_unavailable',
          ),
        ),
      );
    },
  );

  test(
    'system picker cancellation stays empty and camera cancellation is null',
    () async {
      final adapter = FakePicker();
      final picker = DwySystemMediaPicker.withAdapter(adapter);
      expect(await picker.pickImages(), isEmpty);
      expect(await picker.pickMedia(multiple: true), isEmpty);
      expect(await picker.takePhoto(), isNull);
    },
  );

  test('system picker preserves files and exposes stream instead of permanent path', () async {
    final file = FakeFile();
    final adapter = FakePicker()..files = [file];
    final picker = DwySystemMediaPicker.withAdapter(adapter);
    final files = await picker.pickImages(multiple: true);
    expect(files.single, same(file));
    expect(await files.single.openRead().expand((bytes) => bytes).toList(), [
      1,
      2,
      3,
    ]);
    expect(await files.single.length(), 3);
    expect(adapter.lastMultiple, isTrue);
  });

  test(
    'Android lost data has an explicit recovery entry and is not a new pick',
    () async {
      final adapter = FakePicker()..lostFiles = [FakeFile()];
      final picker = DwySystemMediaPicker.withAdapter(adapter);
      expect(await picker.recoverLostData(), hasLength(1));
      expect(adapter.recoverCount, 1);
      expect(adapter.pickCount, 0);
    },
  );

  test('platform failures retain code and cause without masquerading as cancellation', () async {
    final failure = PlatformException(
      code: 'camera_access_denied',
      message: 'Native details',
    );
    final adapter = FakePicker()..failure = failure;
    final picker = DwySystemMediaPicker.withAdapter(adapter);
    await expectLater(
      picker.takePhoto(),
      throwsA(
        isA<DwyMediaException>()
            .having((e) => e.code, 'code', 'camera_access_denied')
            .having((e) => e.cause, 'cause', same(failure)),
      ),
    );
    adapter.failure = PlatformException(code: 'lost_data_error');
    await expectLater(
      picker.recoverLostData(),
      throwsA(isA<DwyMediaException>()),
    );
  });
}

DwyMediaAsset asset(int value) => DwyMediaAsset(
  id: '$value',
  kind: DwyMediaKind.images,
  width: 100,
  height: 100,
  duration: Duration.zero,
);

class FakeLibrary implements DwyPhotoLibraryAdapter {
  DwyMediaAccess access = DwyMediaAccess.authorized;
  int requestCount = 0;
  int listCount = 0;
  int pageCount = 0;
  int thumbnailCount = 0;
  int manageCount = 0;
  DwyMediaKind? lastKind;

  @override
  Future<DwyMediaAccess> permission(DwyMediaKind kind) async => access;
  @override
  Future<DwyMediaAccess> requestAccess(DwyMediaKind kind) async {
    requestCount++;
    return access;
  }

  @override
  Future<void> manageLimitedAccess(DwyMediaKind kind) async {
    manageCount++;
    access = DwyMediaAccess.authorized;
  }

  @override
  Future<List<DwyAlbum>> albums(DwyMediaKind kind) async {
    listCount++;
    lastKind = kind;
    return [
      DwyAlbum(id: 'album', name: 'Album', count: 3, kind: kind, isAll: true),
    ];
  }

  @override
  Future<List<DwyMediaAsset>> assets(DwyAlbum album, int page, int size) async {
    pageCount++;
    return List.generate(3, asset).skip(page * size).take(size).toList();
  }

  @override
  Future<Uint8List?> thumbnail(
    DwyMediaAsset asset,
    int width,
    int height,
  ) async {
    thumbnailCount++;
    return Uint8List.fromList([1]);
  }

  @override
  Future<DwyMediaFile?> open(DwyMediaAsset asset) async => null;
}

class FakePicker implements DwySystemMediaPickerAdapter {
  List<DwyMediaFile> files = [];
  List<DwyMediaFile> lostFiles = [];
  PlatformException? failure;
  int pickCount = 0;
  int recoverCount = 0;
  bool? lastMultiple;

  @override
  Future<List<DwyMediaFile>> pickImages(bool multiple) async {
    pickCount++;
    lastMultiple = multiple;
    return files;
  }

  @override
  Future<List<DwyMediaFile>> pickMedia(bool multiple) async => files;

  @override
  Future<DwyMediaFile?> takePhoto() async {
    if (failure != null) throw failure!;
    return files.firstOrNull;
  }

  @override
  Future<List<DwyMediaFile>> recoverLostData() async {
    recoverCount++;
    if (failure != null) throw failure!;
    return lostFiles;
  }
}

class FakeFile implements DwyMediaFile {
  @override
  String get name => 'sample.jpg';
  @override
  Future<int> length() async => 3;
  @override
  Stream<List<int>> openRead() => Stream.value([1, 2, 3]);
  @override
  Future<Uint8List> readAsBytes() async => Uint8List.fromList([1, 2, 3]);
}
