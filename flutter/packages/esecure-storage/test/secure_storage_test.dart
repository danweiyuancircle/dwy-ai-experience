import 'package:dwy_secure_storage/dwy_secure_storage.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  late _MemorySecrets backend;
  late DwySecureStorage secrets;
  setUp(() {
    backend = _MemorySecrets();
    secrets = DwySecureStorage(
      product: 'example',
      account: 'first',
      storage: backend,
    );
  });

  test('round trips secrets and removes a single key', () async {
    expect(await secrets.read('token'), isNull);
    await secrets.write('token', 'test-secret');
    expect(await secrets.read('token'), 'test-secret');
    await secrets.remove('token');
    expect(await secrets.read('token'), isNull);
  });

  test('clear preserves other accounts, products and native keys', () async {
    final account = DwySecureStorage(
      product: 'example',
      account: 'first-other',
      storage: backend,
    );
    final product = DwySecureStorage(
      product: 'example.other',
      account: 'first',
      storage: backend,
    );
    backend.values['native.credential'] = 'test-native';
    await secrets.write('token', 'test-first');
    await account.write('token', 'test-second');
    await product.write('token', 'test-other');
    await secrets.clear();
    expect(await secrets.read('token'), isNull);
    expect(await account.read('token'), 'test-second');
    expect(await product.read('token'), 'test-other');
    expect(backend.values['native.credential'], 'test-native');
    expect(backend.globalDeleteCalls, 0);
  });

  test('scope encoding cannot collide through separators', () async {
    final a = DwySecureStorage(product: 'a.b', account: 'c', storage: backend);
    final b = DwySecureStorage(product: 'a', account: 'b.c', storage: backend);
    await a.write('same', 'one');
    await b.write('same', 'two');
    expect(await a.read('same'), 'one');
    expect(await b.read('same'), 'two');
  });

  test('invalid names are rejected and platform failures propagate', () async {
    expect(
      () => DwySecureStorage(product: '', account: 'x', storage: backend),
      throwsArgumentError,
    );
    expect(() => secrets.read('bad\nkey'), throwsArgumentError);
    backend.failure = StateError('platform locked');
    await expectLater(secrets.write('token', 'test-secret'), throwsStateError);
    await expectLater(secrets.clear(), throwsStateError);
  });
}

// Typed futures preserve the plugin contract without invoking the real platform store.
class _MemorySecrets extends Fake implements FlutterSecureStorage {
  final values = <String, String>{};
  Object? failure;
  int globalDeleteCalls = 0;

  @override
  dynamic noSuchMethod(Invocation invocation) {
    final key = invocation.namedArguments[#key] as String?;
    if (invocation.memberName == #read) {
      return failure == null
          ? Future<String?>.value(values[key])
          : Future<String?>.error(failure!);
    }
    if (invocation.memberName == #readAll) {
      return failure == null
          ? Future<Map<String, String>>.value(Map.of(values))
          : Future<Map<String, String>>.error(failure!);
    }
    if (invocation.memberName == #write || invocation.memberName == #delete) {
      if (failure != null) return Future<void>.error(failure!);
      if (invocation.memberName == #write) {
        values[key!] = invocation.namedArguments[#value] as String;
      } else {
        values.remove(key);
      }
      return Future<void>.value();
    }
    if (invocation.memberName == #deleteAll) {
      globalDeleteCalls++;
      return Future<void>.error(StateError('global deletion is forbidden'));
    }
    return super.noSuchMethod(invocation);
  }
}
