import 'package:material_ui/material_ui.dart';

/// A controlled form input. The caller owns and disposes controller/focusNode;
/// validation and localized labels are supplied by the consuming feature.
class DwyTextField extends StatelessWidget {
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
  final TextInputAction? textInputAction;
  final IconData? prefixIcon;
  final String? clearLabel;
  final bool enabled;
  final bool obscureText;
  final int maxLines;
  final AutovalidateMode autovalidateMode;

  @override
  Widget build(BuildContext context) =>
      ValueListenableBuilder<TextEditingValue>(
        valueListenable: controller,
        builder: (context, value, _) => TextFormField(
          controller: controller,
          focusNode: focusNode,
          enabled: enabled,
          obscureText: obscureText,
          maxLines: maxLines,
          keyboardType: keyboardType,
          textInputAction: textInputAction,
          validator: validator,
          autovalidateMode: autovalidateMode,
          onChanged: onChanged,
          onFieldSubmitted: onSubmitted,
          decoration: InputDecoration(
            labelText: label,
            hintText: hintText,
            helperText: helperText,
            errorText: errorText,
            errorMaxLines: 3,
            prefixIcon: prefixIcon == null ? null : Icon(prefixIcon),
            suffixIcon: clearLabel != null && value.text.isNotEmpty
                ? IconButton(
                    tooltip: clearLabel,
                    onPressed: enabled
                        ? () {
                            controller.clear();
                            onChanged?.call('');
                          }
                        : null,
                    icon: const Icon(Icons.close),
                  )
                : null,
          ),
        ),
      );
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
  Widget build(BuildContext context) => DwyTextField(
    controller: controller,
    hintText: hintText,
    clearLabel: clearLabel,
    onChanged: onChanged,
    onSubmitted: onSubmitted,
    enabled: enabled,
    prefixIcon: Icons.search,
    textInputAction: TextInputAction.search,
  );
}
