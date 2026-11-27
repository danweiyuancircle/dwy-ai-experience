import 'dart:async';
import 'dart:io';

// Drift's background isolate wraps migration errors; this pinned API lets the
// test verify the original failure without weakening the assertion to any error.
// ignore: experimental_member_use
import 'package:drift/remote.dart' show DriftRemoteException;
import 'package:dwy_database/dwy_database.dart';
import 'package:test/test.dart';

import '../example/note_database.dart';

void main() {
  late Directory temporary;
  late File file;
  setUp(() async {
    temporary = await Directory.systemTemp.createTemp('dwy-database-test-');
    file = File('${temporary.path}/account/notes.sqlite');
  });
  tearDown(() async {
    await temporary.delete(recursive: true);
  });

  Future<DwyDatabase<ExampleNoteDatabase>> open() =>
      DwyDatabase.open(file: file, create: ExampleNoteDatabase.new);

  test('file data survives close and reopening; close is idempotent', () async {
    final first = await open();
    await first.database.addNote('persisted');
    final close = first.close();
    expect(identical(close, first.close()), true);
    await close;
    expect(() => first.database, throwsStateError);
    final second = await open();
    try {
      expect(
        (await second.database.select(second.database.exampleNotes).get())
            .single
            .body,
        'persisted',
      );
    } finally {
      await second.close();
    }
  });

  test(
    'transaction failure rolls back instead of leaving a partial write',
    () async {
      final owner = await open();
      try {
        await expectLater(
          owner.transaction<void>((db) async {
            await db.addNote('must roll back');
            throw StateError('cancel business operation');
          }),
          throwsStateError,
        );
        expect(
          await owner.database.select(owner.database.exampleNotes).get(),
          isEmpty,
        );
      } finally {
        await owner.close();
      }
    },
  );

  test('product query stream observes committed writes', () async {
    final owner = await open();
    final events = StreamIterator(owner.database.watchNotes());
    try {
      expect(await events.moveNext().timeout(const Duration(seconds: 5)), true);
      expect(events.current, isEmpty);
      await owner.database.addNote('new');
      expect(await events.moveNext().timeout(const Duration(seconds: 5)), true);
      expect(events.current.single.body, 'new');
    } finally {
      await events.cancel();
      await owner.close();
    }
  });

  test('migration preserves old records and adds default values', () async {
    final old = await DwyDatabase.open(
      file: file,
      create: (executor) => ExampleNoteDatabase(executor, version: 1),
    );
    await old.database.customStatement(
      'INSERT INTO example_notes(body) VALUES (?)',
      ['before upgrade'],
    );
    await old.close();
    final migrated = await open();
    try {
      final note =
          (await migrated.database.select(migrated.database.exampleNotes).get())
              .single;
      expect(note.body, 'before upgrade');
      expect(note.pinned, false);
    } finally {
      await migrated.close();
    }
  });

  test(
    'failed migration closes resources without erasing existing records',
    () async {
      final old = await DwyDatabase.open(
        file: file,
        create: (executor) => ExampleNoteDatabase(executor, version: 1),
      );
      await old.database.customStatement(
        'INSERT INTO example_notes(body) VALUES (?)',
        ['keep'],
      );
      await old.close();
      await expectLater(
        DwyDatabase.open(
          file: file,
          create: (executor) =>
              ExampleNoteDatabase(executor, failMigration: true),
        ),
        throwsA(
          isA<DriftRemoteException>().having(
            (error) => error.remoteCause.toString(),
            'remoteCause',
            'Bad state: Example migration failure',
          ),
        ),
      );
      final reopened = await DwyDatabase.open(
        file: file,
        create: (executor) => ExampleNoteDatabase(executor, version: 1),
      );
      try {
        final rows = await reopened.database
            .customSelect('SELECT body FROM example_notes')
            .get();
        expect(rows.single.read<String>('body'), 'keep');
      } finally {
        await reopened.close();
      }
    },
  );
}
