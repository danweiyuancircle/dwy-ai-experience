import 'dart:ui' show lerpDouble;

import 'package:material_ui/material_ui.dart';

/// Product-independent geometry. Flutter text scaling remains enabled.
@immutable
class DwyTokens extends ThemeExtension<DwyTokens> {
  const DwyTokens({
    this.controlRadius = 12,
    this.groupRadius = 16,
    this.controlHeight = 48,
    this.pageInset = 24,
  }) : assert(controlRadius >= 0),
       assert(groupRadius >= 0),
       assert(controlHeight >= 48),
       assert(pageInset >= 0);

  static const double spaceXS = 4;
  static const double spaceS = 8;
  static const double spaceM = 12;
  static const double spaceL = 16;
  static const double spaceXL = 24;

  final double controlRadius;
  final double groupRadius;
  final double controlHeight;
  final double pageInset;

  @override
  DwyTokens copyWith({
    double? controlRadius,
    double? groupRadius,
    double? controlHeight,
    double? pageInset,
  }) => DwyTokens(
    controlRadius: controlRadius ?? this.controlRadius,
    groupRadius: groupRadius ?? this.groupRadius,
    controlHeight: controlHeight ?? this.controlHeight,
    pageInset: pageInset ?? this.pageInset,
  );

  @override
  DwyTokens lerp(covariant DwyTokens? other, double t) {
    if (other == null) return this;
    return DwyTokens(
      controlRadius: lerpDouble(controlRadius, other.controlRadius, t)!,
      groupRadius: lerpDouble(groupRadius, other.groupRadius, t)!,
      controlHeight: lerpDouble(controlHeight, other.controlHeight, t)!,
      pageInset: lerpDouble(pageInset, other.pageInset, t)!,
    );
  }
}
