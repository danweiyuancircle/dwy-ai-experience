import 'dart:io';

import 'package:dwy_component_gallery/catalog/catalog.dart';
import 'package:flutter_test/flutter_test.dart';

// flutter test runs with the package root as the working directory.
const _packageRoots = {
  'dwy_design': '../../packages/edesign',
  'dwy_image': '../../packages/eimage',
};

/// Public Dwy* types and showDwy* entry points reachable from the package barrel.
Set<String> _exportedSymbols(String package) {
  final root = _packageRoots[package]!;
  final barrel = File('$root/lib/$package.dart').readAsStringSync();
  final symbols = <String>{};
  for (final export in RegExp(
    r"^export 'src/(\w+\.dart)';",
    multiLine: true,
  ).allMatches(barrel)) {
    final source = File('$root/lib/src/${export[1]}').readAsStringSync();
    symbols
      ..addAll(
        RegExp(
          r'^(?:(?:abstract|final|base|sealed|interface) )*(?:class|enum|mixin|typedef) (Dwy\w+)',
          multiLine: true,
        ).allMatches(source).map((match) => match[1]!),
      )
      ..addAll(
        RegExp(
          r'^\S+ (showDwy\w+)[<(]',
          multiLine: true,
        ).allMatches(source).map((match) => match[1]!),
      );
  }
  return symbols;
}

void main() {
  for (final package in _packageRoots.keys) {
    group(package, () {
      final exported = _exportedSymbols(package);
      final covered = {
        for (final entry in galleryCatalog)
          if (entry.package == package) ...entry.symbols,
      };

      test('every public export has a catalog entry', () {
        expect(exported.difference(covered), isEmpty);
      });

      test('catalog lists no symbol that is no longer exported', () {
        expect(covered.difference(exported), isEmpty);
      });
    });
  }

  // Guards the regular expressions above: an empty scan would pass vacuously.
  test('export scan sees representative symbols', () {
    expect(_exportedSymbols('dwy_design'), contains('DwyButton'));
    expect(_exportedSymbols('dwy_design'), contains('showDwySheet'));
    expect(_exportedSymbols('dwy_image'), contains('DwyImage'));
  });

  group('catalog entries', () {
    test('ids and names are unique', () {
      final ids = {for (final entry in galleryCatalog) entry.id};
      final names = {for (final entry in galleryCatalog) entry.name};
      expect(ids.length, galleryCatalog.length);
      expect(names.length, galleryCatalog.length);
    });

    for (final entry in galleryCatalog) {
      test(
        '${entry.name} documents purpose, capabilities and a Dart example',
        () {
          expect(entry.summary, isNotEmpty);
          expect(entry.capabilities, isNotEmpty);
          expect(entry.constraints, isNotEmpty);
          expect(entry.symbols, contains(entry.name));
          expect(entry.code, contains(entry.name));
          expect(
            {for (final state in entry.states) state.id}.length,
            entry.states.length,
          );
        },
      );
    }
  });
}
