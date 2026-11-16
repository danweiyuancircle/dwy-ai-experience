import 'dart:async';
import 'dart:typed_data';

import 'package:dwy_design/dwy_design.dart';
import 'package:dwy_image/dwy_image.dart';
import 'package:material_ui/material_ui.dart';

import 'sample_image.dart';

/// Public image API examples. Network access starts only after an explicit Load;
/// no authentication headers or external demonstration domains are configured.
class ImageExamples extends StatefulWidget {
  const ImageExamples({super.key});

  @override
  State<ImageExamples> createState() => _ImageExamplesState();
}

class _ImageExamplesState extends State<ImageExamples> {
  static var _nextOwner = 0;
  final _owner = _nextOwner++;
  final _url = TextEditingController();
  final _asset = DwyImageSource.asset('assets/sample.png');
  final _memory = DwyImageSource.memory(galleryImageBytes);
  final _invalid = DwyImageSource.memory(Uint8List.fromList([0, 1, 2]));
  final Map<String, DwyImageCache> _caches = {};
  DwyImageSource? _network;
  Future<void>? _clearing;
  var _scope = 'a';
  var _decodeSize = 192.0;
  var _radius = 12.0;
  var _repaired = false;
  var _busy = false;
  var _status = '';

  @override
  void dispose() {
    _url.dispose();
    // State disposal cannot await. Retain the current maintenance chain, then
    // close every owned cache after descendants have released image listeners.
    unawaited(_close());
    super.dispose();
  }

  Future<void> _close() async {
    await _clearing;
    for (final cache in _caches.values) {
      try {
        await cache.clear();
      } catch (error, stack) {
        _reportClosingError(error, stack);
      }
      try {
        await cache.dispose();
      } catch (error, stack) {
        _reportClosingError(error, stack);
      }
    }
  }

  void _reportClosingError(Object error, StackTrace stack) =>
      FlutterError.reportError(
        FlutterErrorDetails(
          exception: error,
          stack: stack,
          library: 'component_gallery',
          context: ErrorDescription(
            'while closing the image demonstration caches',
          ),
        ),
      );

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      const Text('资源和内存示例无需网络。网络示例仅在你输入地址并点击加载后发起请求。'),
      const SizedBox(height: 20),
      Text('外观与解码', style: Theme.of(context).textTheme.titleMedium),
      Text('物理解码上限：${_decodeSize.round()} px'),
      Slider(
        value: _decodeSize,
        min: 48,
        max: 384,
        divisions: 7,
        label: '${_decodeSize.round()} px',
        onChanged: (value) => setState(() => _decodeSize = value),
      ),
      Text('圆角：${_radius.round()}'),
      Slider(
        value: _radius,
        min: 0,
        max: 32,
        divisions: 8,
        onChanged: (value) => setState(() => _radius = value),
      ),
      LayoutBuilder(
        builder: (context, constraints) {
          final width = constraints.maxWidth.clamp(48.0, 260.0).toDouble();
          return Wrap(
            spacing: 20,
            runSpacing: 20,
            children: [
              _sample('Asset 资源', _asset, width),
              _sample('Memory 内存', _memory, width),
              _sample(
                '失败与重试',
                _repaired ? _memory : _invalid,
                width,
                showErrorDemo: true,
              ),
            ],
          );
        },
      ),
      const SizedBox(height: 16),
      DwyButton(
        label: _repaired ? '恢复无效演示数据' : '修复演示数据',
        variant: DwyButtonVariant.secondary,
        onPressed: () => setState(() => _repaired = !_repaired),
      ),
      if (_repaired)
        const Padding(padding: EdgeInsets.only(top: 8), child: Text('已换成有效图片')),
      const SizedBox(height: 32),
      Text('网络与 scope 隔离', style: Theme.of(context).textTheme.titleMedium),
      const SizedBox(height: 12),
      const Text('可用 tool/image_fixture.dart 启动本机服务。不要在演示地址中填写凭据或敏感内容。'),
      const SizedBox(height: 12),
      DwyTextField(
        key: const Key('image-url'),
        controller: _url,
        label: '图片 URL',
        hintText: 'http://127.0.0.1:5189/image.png',
        keyboardType: TextInputType.url,
        enabled: !_busy,
        onSubmitted: (_) => _load(),
      ),
      const SizedBox(height: 16),
      Wrap(
        spacing: 12,
        runSpacing: 12,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          DropdownButton<String>(
            value: _scope,
            items: const [
              DropdownMenuItem(value: 'a', child: Text('Scope A')),
              DropdownMenuItem(value: 'b', child: Text('Scope B')),
            ],
            onChanged: _busy
                ? null
                : (value) => setState(() {
                    _scope = value!;
                    _network = null;
                    _status = '已切换 scope，请点击加载。';
                  }),
          ),
          DwyButton(label: '加载网络图片', onPressed: _busy ? null : _load),
          DwyButton(
            label: '清理当前 scope',
            variant: DwyButtonVariant.secondary,
            loading: _busy,
            onPressed: _busy ? null : () => _clearing = _clear(),
          ),
        ],
      ),
      const SizedBox(height: 16),
      if (_network case final source?)
        LayoutBuilder(
          builder: (context, constraints) => Align(
            alignment: Alignment.centerLeft,
            child: _image(
              source,
              constraints.maxWidth.clamp(48.0, 320.0).toDouble(),
            ),
          ),
        )
      else
        const Text('网络图片尚未加载'),
      if (_status.isNotEmpty)
        Padding(padding: const EdgeInsets.only(top: 12), child: Text(_status)),
      const SizedBox(height: 12),
      const Text(
        '清理先移除当前图片，再等待当前 scope 缓存维护完成。另一 scope 的缓存不受影响。Web 上游实现不提供同等磁盘缓存，移动端需另验。',
      ),
    ],
  );

  Widget _sample(
    String label,
    DwyImageSource source,
    double width, {
    bool showErrorDemo = false,
  }) => SizedBox(
    width: width,
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label),
        const SizedBox(height: 8),
        _image(source, width, showErrorDemo: showErrorDemo),
      ],
    ),
  );

  Widget _image(
    DwyImageSource source,
    double width, {
    bool showErrorDemo = false,
  }) => DwyImage(
    source: source,
    width: width,
    height: 160,
    cacheWidth: _decodeSize.round(),
    cacheHeight: _decodeSize.round(),
    borderRadius: BorderRadius.circular(_radius),
    semanticLabel: 'DWY 图片示例',
    loadingLabel: '正在加载图片',
    errorLabel: '图片暂不可用',
    retryLabel: '重试加载',
    placeholderBuilder: (_) => const Center(child: Text('正在加载图片')),
    errorBuilder: (context, error, retry) => Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              showErrorDemo ? '示例数据暂不可解码' : '图片暂不可用',
              textAlign: TextAlign.center,
            ),
            TextButton(
              onPressed: retry,
              child: Text(showErrorDemo ? '重试解码' : '重试加载'),
            ),
          ],
        ),
      ),
    ),
  );

  void _load() {
    if (_busy) return;
    final uri = Uri.tryParse(_url.text.trim());
    if (uri == null ||
        !uri.hasAuthority ||
        uri.host.isEmpty ||
        !['http', 'https'].contains(uri.scheme) ||
        uri.userInfo.isNotEmpty ||
        uri.hasFragment) {
      setState(() => _status = '请输入不含账户信息和片段的完整 HTTP(S) 图片地址。');
      return;
    }
    final cache = _caches.putIfAbsent(
      _scope,
      () => DwyImageCache(namespace: 'component_gallery_${_owner}_$_scope'),
    );
    setState(() {
      _network = DwyImageSource.network(uri, cache: cache);
      _status = '使用 Scope ${_scope.toUpperCase()}；加载失败可点击图片内的重试。';
    });
  }

  Future<void> _clear() async {
    final cache = _caches[_scope];
    if (cache == null) {
      setState(() => _status = '当前 scope 尚未创建网络缓存。');
      return;
    }
    setState(() {
      _network = null;
      _busy = true;
      _status = '正在清理当前 scope…';
    });
    try {
      await WidgetsBinding.instance.endOfFrame;
      await cache.clear();
      if (mounted) setState(() => _status = '当前 scope 已清理，另一 scope 保留。');
    } catch (_) {
      if (mounted) setState(() => _status = '缓存清理失败，请重试。');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }
}
