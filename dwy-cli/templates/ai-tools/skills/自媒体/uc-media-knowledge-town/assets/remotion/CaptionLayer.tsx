import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import type {CueTimeline} from './CueTimeline';

export const CaptionLayer: React.FC<{timeline: CueTimeline}> = ({timeline}) => {
  const frame = useCurrentFrame();
  const cue = timeline.cues.find((item) => frame >= item.startFrame && frame < item.endFrame);
  if (!cue) return null;
  const opacity = interpolate(frame, [cue.startFrame, cue.startFrame + 4], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <div style={{position: 'absolute', left: 220, right: 220, bottom: 42, minHeight: 112, zIndex: 50, opacity, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '18px 42px', color: '#14213d', background: '#fffdf5', border: '7px solid #14213d', borderRadius: 32, boxShadow: '0 12px 0 #14213d', fontFamily: 'Arial, PingFang SC, sans-serif', fontSize: 46, fontWeight: 900, lineHeight: 1.25, textAlign: 'center'}}>
      {cue.caption.text}
    </div>
  );
};
