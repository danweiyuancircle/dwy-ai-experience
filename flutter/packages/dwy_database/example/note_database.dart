import 'package:drift/drift.dart';

part 'note_database.g.dart';

/// Example product-owned schema. This is not a shared business table.
class ExampleNotes extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get body => text()();
  BoolColumn get pinned => boolean().withDefault(const Constant(false))();
}

/// Product-owned schema and migration example, also exercised against real files.
/// Run build_runner to generate the Drift implementation; no generated code is hand-written.
@DriftDatabase(tables: [ExampleNotes])
class ExampleNoteDatabase extends _$ExampleNoteDatabase {
  ExampleNoteDatabase(
    QueryExecutor executor, {
    this.version = 2,
    this.failMigration = false,
  }) : super(executor);
  final int version;
  final bool failMigration;

  @override
  int get schemaVersion => version;

  @override
  MigrationStrategy get migration => MigrationStrategy(
    onCreate: (migrator) async {
      if (version == 1) {
        await customStatement(
          'CREATE TABLE example_notes (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, body TEXT NOT NULL)',
        );
      } else {
        await migrator.createAll();
      }
    },
    onUpgrade: (migrator, from, to) async {
      if (failMigration) throw StateError('Example migration failure');
      if (from != 1 || to != 2)
        throw UnsupportedError('No migration for $from to $to');
      await transaction(
        () => migrator.addColumn(exampleNotes, exampleNotes.pinned),
      );
    },
    beforeOpen: (_) async {
      await customStatement('PRAGMA foreign_keys = ON');
    },
  );

  /// Product query keeps typed rows and reactive invalidation provided by Drift.
  Stream<List<ExampleNote>> watchNotes() => select(exampleNotes).watch();

  /// Example insertion; the returned future completes after SQLite accepts the write.
  Future<int> addNote(String body) =>
      into(exampleNotes).insert(ExampleNotesCompanion.insert(body: body));
}
