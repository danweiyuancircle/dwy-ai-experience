import 'package:dwy_design/dwy_design.dart';
import 'package:flutter/widgets.dart';

import 'app/gallery_app.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await DwyGlass.initialize();
  runApp(const GalleryApp());
}
