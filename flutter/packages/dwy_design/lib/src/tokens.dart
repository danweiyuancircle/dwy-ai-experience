import 'package:flutter/foundation.dart';

/// Product-independent geometry. Flutter text scaling remains enabled.
@immutable
class DwyTokens {
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

  /// Returns geometry with the supplied dimensions replaced.
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
}
