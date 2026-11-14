import XCTest
import SwiftUI
@testable import DesignCore

final class MotionTests: XCTestCase {
    func testReducedMotionDisablesEveryPresetAnimation() {
        for preset in EMotionPreset.allCases {
            XCTAssertNil(preset.animation(reduceMotion: true), "\(preset) 不能绕过系统减少动态效果设置")
            XCTAssertNotNil(preset.animation(reduceMotion: false))
        }
    }

    func testSemanticPresetsReuseExistingMotionTokens() {
        XCTAssertEqual(EMotionPreset.selection.animation(reduceMotion: false), Motion.snappy)
        XCTAssertEqual(EMotionPreset.reorder.animation(reduceMotion: false), Motion.spring)
        XCTAssertEqual(EMotionPreset.page.animation(reduceMotion: false), Motion.page)
        XCTAssertEqual(EMotionPreset.feedback.animation(reduceMotion: false), Motion.soft)
    }

    func testReducedTransitionsKeepFadeAndRemoveMovement() {
        XCTAssertEqual(EMotionTransition.softMove.resolved(reduceMotion: false), .softMove)
        XCTAssertEqual(EMotionTransition.softMove.resolved(reduceMotion: true), .fade)
        XCTAssertEqual(EMotionTransition.fade.resolved(reduceMotion: true), .fade)
    }

    @MainActor
    func testPublicModifiersAndLegacyPressStyleRemainComposable() {
        let _ = Text("Status").eMotion(.selection, value: true).eTransition(.softMove)
        let _ = Button("Action") {}.scalePress()
        let _ = ScalePressButtonStyle()
        XCTAssertNotEqual(Motion.press, Motion.page)
    }
}
