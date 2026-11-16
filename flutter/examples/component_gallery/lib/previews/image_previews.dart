import 'package:dwy_design/dwy_design.dart';
import 'package:dwy_image/dwy_image.dart';
import 'package:material_ui/material_ui.dart';
import 'package:flutter/widget_previews.dart';

import '../features/gallery/sample_image.dart';

/// Memory-only preview: no cache manager, disk file or network/plugin call.
@Preview(name: 'Memory / light', group: 'DWY Images', size: Size(360, 260))
Widget galleryImageLightPreview() => _preview(Brightness.light);

/// Same image API and geometry under the dark DWY theme.
@Preview(name: 'Memory / dark', group: 'DWY Images', size: Size(360, 260))
Widget galleryImageDarkPreview() => _preview(Brightness.dark);

Widget _preview(Brightness brightness) => MaterialApp(
  debugShowCheckedModeBanner: false,
  theme: DwyTheme.create(brightness: brightness),
  home: Scaffold(
    body: Center(
      child: DwyImage(
        source: DwyImageSource.memory(galleryImageBytes),
        width: 280,
        height: 180,
        borderRadius: BorderRadius.circular(16),
        semanticLabel: 'DWY 图片预览',
        loadingLabel: '正在加载图片',
        errorLabel: '图片暂不可用',
        retryLabel: '重试',
      ),
    ),
  ),
);
