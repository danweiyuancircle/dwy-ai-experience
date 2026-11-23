import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {AudioTracks} from './AudioTracks';
import {CaptionLayer} from './CaptionLayer';
import type {CueTimeline} from './CueTimeline';

export const KnowledgeTownComposition: React.FC<{
  timeline: CueTimeline;
  bgmFile: string;
  renderVisual: (action: string, frame: number) => React.ReactNode;
}> = ({timeline, bgmFile, renderVisual}) => {
  const frame = useCurrentFrame();
  const cue = timeline.cues.find((item) => frame >= item.startFrame && frame < item.endFrame);
  return (
    <AbsoluteFill style={{background: '#f4e8c6', overflow: 'hidden'}}>
      {renderVisual(cue?.visual.action ?? 'hold', frame)}
      <CaptionLayer timeline={timeline} />
      <AudioTracks timeline={timeline} bgmFile={bgmFile} />
    </AbsoluteFill>
  );
};
