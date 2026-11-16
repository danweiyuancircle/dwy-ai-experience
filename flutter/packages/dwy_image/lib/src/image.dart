import 'package:material_ui/material_ui.dart';

import 'source.dart';

/// Application-owned loading presentation; dimensions are constrained by DwyImage.
typedef DwyImagePlaceholderBuilder = Widget Function(BuildContext context);

/// Shows an external image/cache error. Do not expose raw error text to users;
/// use the provided retry callback after presenting an appropriate message.
typedef DwyImageErrorBuilder = Widget Function(
  BuildContext context,
  Object error,
  VoidCallback retry,
);

/// Fixed-size image with theme-aware loading/error states and scoped retry.
/// Width and height are logical pixels. Decode size defaults to physical display
/// pixels; explicitly set a bound when showing a cropped high-resolution image.
final class DwyImage extends StatefulWidget {
  const DwyImage({
    super.key,
    required this.source,
    required this.width,
    required this.height,
    this.fit = BoxFit.cover,
    this.borderRadius = BorderRadius.zero,
    this.semanticLabel,
    this.cacheWidth,
    this.cacheHeight,
    this.placeholderBuilder,
    this.errorBuilder,
    this.fadeDuration = const Duration(milliseconds: 150),
    this.loadingLabel = 'Loading image',
    this.errorLabel = 'Image unavailable',
    this.retryLabel = 'Retry',
  }) : assert(width > 0 && width < double.infinity),
       assert(height > 0 && height < double.infinity),
       assert(cacheWidth == null || cacheWidth > 0),
       assert(cacheHeight == null || cacheHeight > 0);

  final DwyImageSource source;
  final double width;
  final double height;
  final BoxFit fit;
  final BorderRadius borderRadius;
  final String? semanticLabel;
  final int? cacheWidth;
  final int? cacheHeight;
  final DwyImagePlaceholderBuilder? placeholderBuilder;
  final DwyImageErrorBuilder? errorBuilder;
  final Duration fadeDuration;
  final String loadingLabel;
  final String errorLabel;
  final String retryLabel;

  @override
  State<DwyImage> createState() => _DwyImageState();
}

final class _DwyImageState extends State<DwyImage> {
  var _revision = 0;
  var _retrying = false;
  Object? _maintenanceError;

  @override
  void didUpdateWidget(DwyImage oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.source != widget.source) {
      _revision++;
      _maintenanceError = null;
      _retrying = false;
    }
  }

  Future<void> _retry() async {
    if (_retrying) return;
    final source = widget.source;
    setState(() {
      _retrying = true;
      _maintenanceError = null;
    });
    try {
      await source.invalidate();
      if (!mounted || widget.source != source) return;
      setState(() {
        _revision++;
        _retrying = false;
      });
    } catch (error) {
      // Cache I/O is an external boundary; a failed eviction remains visible.
      if (!mounted || widget.source != source) return;
      setState(() {
        _maintenanceError = error;
        _retrying = false;
      });
    }
  }

  Widget _loading(BuildContext context) =>
      widget.placeholderBuilder?.call(context) ??
      Semantics(
        label: widget.loadingLabel,
        child: const Center(
          child: SizedBox.square(
            dimension: 20,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
        ),
      );

  Widget _failed(BuildContext context, Object error) =>
      widget.errorBuilder?.call(context, error, _retry) ??
      Center(
        child: Tooltip(
          message: widget.errorLabel,
          child: TextButton(
            onPressed: _retry,
            child: Text(
              widget.retryLabel,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ),
      );

  @override
  Widget build(BuildContext context) {
    final ratio = MediaQuery.devicePixelRatioOf(context);
    final width = widget.cacheWidth ?? (widget.width * ratio).ceil();
    final height = widget.cacheHeight ?? (widget.height * ratio).ceil();
    final Widget content;
    if (_retrying) {
      content = _loading(context);
    } else if (_maintenanceError case final error?) {
      content = _failed(context, error);
    } else {
      content = Image(
        key: ValueKey(_revision),
        image: widget.source.provider(cacheWidth: width, cacheHeight: height),
        width: widget.width,
        height: widget.height,
        fit: widget.fit,
        excludeFromSemantics: true,
        frameBuilder: (context, image, frame, synchronous) {
          if (synchronous) return image;
          if (frame == null) return _loading(context);
          return TweenAnimationBuilder<double>(
            tween: Tween(begin: 0, end: 1),
            duration: MediaQuery.disableAnimationsOf(context)
                ? Duration.zero
                : widget.fadeDuration,
            builder: (context, value, child) =>
                Opacity(opacity: value, child: child),
            child: image,
          );
        },
        errorBuilder: (context, error, stack) => _failed(context, error),
      );
    }
    return Semantics(
      image: true,
      label: widget.semanticLabel,
      child: ClipRRect(
        borderRadius: widget.borderRadius,
        child: SizedBox(
          width: widget.width,
          height: widget.height,
          child: ColoredBox(
            color: Theme.of(context).colorScheme.surfaceContainerLow,
            child: content,
          ),
        ),
      ),
    );
  }
}
