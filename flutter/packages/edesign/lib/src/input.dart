import 'package:cupertino_ui/cupertino_ui.dart';

import 'theme.dart';

/// A controlled form input. The caller owns and disposes controller/focusNode;
/// validation and localized labels are supplied by the consuming feature.
class DwyTextField extends StatefulWidget {
  const DwyTextField({
    required this.controller,
    this.label,
    this.hintText,
    this.helperText,
    this.errorText,
    this.validator,
    this.onChanged,
    this.onSubmitted,
    this.focusNode,
    this.keyboardType,
    this.autofillHints,
    this.maxLength,
    this.textInputAction,
    this.prefixIcon,
    this.clearLabel,
    this.enabled = true,
    this.obscureText = false,
    this.maxLines = 1,
    this.autovalidateMode = AutovalidateMode.disabled,
    super.key,
  }) : assert(!obscureText || maxLines == 1);

  final TextEditingController controller;
  final String? label;
  final String? hintText;
  final String? helperText;
  final String? errorText;
  final FormFieldValidator<String>? validator;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;
  final FocusNode? focusNode;
  final TextInputType? keyboardType;

  /// Platform autofill purposes supplied by the consuming form.
  final Iterable<String>? autofillHints;

  /// Maximum input length enforced by the underlying Cupertino field.
  final int? maxLength;
  final TextInputAction? textInputAction;
  final IconData? prefixIcon;
  final String? clearLabel;
  final bool enabled;
  final bool obscureText;
  final int maxLines;
  final AutovalidateMode autovalidateMode;

  @override
  State<DwyTextField> createState() => _DwyTextFieldState();
}

class _DwyTextFieldState extends State<DwyTextField> {
  late String _initialText = widget.controller.text;

  @override
  void didUpdateWidget(DwyTextField oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.controller != oldWidget.controller) {
      _initialText = widget.controller.text;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = CupertinoTheme.of(context);
    final secondary = CupertinoColors.secondaryLabel.resolveFrom(context);
    final errorColor = CupertinoColors.systemRed.resolveFrom(context);
    final caption = theme.textTheme.textStyle.copyWith(fontSize: 13);
    final radius = DwyTheme.tokensOf(context).controlRadius;
    return FormField<String>(
      key: ObjectKey(widget.controller),
      initialValue: _initialText,
      enabled: widget.enabled,
      autovalidateMode: widget.autovalidateMode,
      validator: widget.validator == null
          ? null
          : (_) => widget.validator!(widget.controller.text),
      onReset: () {
        widget.controller.text = _initialText;
        widget.onChanged?.call(_initialText);
      },
      builder: (field) {
        final error = field.errorText ?? widget.errorText;
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (widget.label case final label?)
              Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: ExcludeSemantics(
                  child: Text(label, style: caption.copyWith(color: secondary)),
                ),
              ),
            Semantics(
              label: widget.label,
              child: ValueListenableBuilder<TextEditingValue>(
                valueListenable: widget.controller,
                builder: (context, value, _) => CupertinoTextField(
                  controller: widget.controller,
                  focusNode: widget.focusNode,
                  enabled: widget.enabled,
                  obscureText: widget.obscureText,
                  maxLines: widget.maxLines,
                  keyboardType: widget.keyboardType,
                  autofillHints: widget.autofillHints,
                  maxLength: widget.maxLength,
                  textInputAction: widget.textInputAction,
                  onChanged: (text) {
                    field.didChange(text);
                    widget.onChanged?.call(text);
                  },
                  onSubmitted: widget.onSubmitted,
                  placeholder: widget.hintText,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 14,
                  ),
                  decoration: BoxDecoration(
                    color: CupertinoColors.secondarySystemGroupedBackground
                        .resolveFrom(context),
                    borderRadius: BorderRadius.circular(radius),
                    border: Border.all(
                      color: error == null
                          ? CupertinoColors.separator.resolveFrom(context)
                          : errorColor,
                    ),
                  ),
                  prefix: widget.prefixIcon == null
                      ? null
                      : Padding(
                          padding: const EdgeInsetsDirectional.only(start: 12),
                          child: Icon(
                            widget.prefixIcon,
                            size: 17,
                            color: secondary,
                          ),
                        ),
                  suffix: widget.clearLabel != null && value.text.isNotEmpty
                      ? Semantics(
                          label: widget.clearLabel,
                          child: CupertinoButton(
                            padding: EdgeInsets.zero,
                            onPressed: widget.enabled
                                ? () {
                                    widget.controller.clear();
                                    field.didChange('');
                                    widget.onChanged?.call('');
                                  }
                                : null,
                            child: const Icon(
                              CupertinoIcons.xmark_circle_fill,
                              size: 17,
                            ),
                          ),
                        )
                      : null,
                ),
              ),
            ),
            if (error != null || widget.helperText != null)
              Padding(
                padding: const EdgeInsets.only(top: 6),
                child: Semantics(
                  liveRegion: error != null,
                  child: Text(
                    error ?? widget.helperText!,
                    style: caption.copyWith(
                      color: error == null ? secondary : errorColor,
                    ),
                  ),
                ),
              ),
          ],
        );
      },
    );
  }
}

/// Search input with an explicit localized clear action; it does not fetch data.
class DwySearchField extends StatelessWidget {
  const DwySearchField({
    required this.controller,
    required this.hintText,
    required this.clearLabel,
    required this.onChanged,
    this.onSubmitted,
    this.enabled = true,
    super.key,
  });

  final TextEditingController controller;
  final String hintText;
  final String clearLabel;
  final ValueChanged<String> onChanged;
  final ValueChanged<String>? onSubmitted;
  final bool enabled;

  @override
  Widget build(BuildContext context) => CupertinoSearchTextField(
    controller: controller,
    placeholder: hintText,
    suffixIcon: Icon(
      CupertinoIcons.xmark_circle_fill,
      semanticLabel: clearLabel,
    ),
    borderRadius: BorderRadius.circular(
      DwyTheme.tokensOf(context).controlRadius,
    ),
    onChanged: onChanged,
    onSubmitted: onSubmitted,
    enabled: enabled,
  );
}
