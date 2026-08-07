import React from 'react';
import {Sequence, staticFile, useCurrentFrame} from 'remotion';
import {Audio} from '@remotion/media';
import type {CueTimeline} from './CueTimeline';

export const AudioTracks: React.FC<{timeline: CueTimeline; bgmFile: string}> = ({timeline, bgmFile}) => {
  const frame = useCurrentFrame();
  const hasVoice = timeline.cues.some((cue) => frame >= cue.startFrame && frame < cue.endFrame);
  return (
    <>
      <Audio src={staticFile(bgmFile)} volume={hasVoice ? 0.06 : 0.18} />
      <Audio src={staticFile(timeline.voice.file)} volume={1} />
      {timeline.cues.flatMap((cue) => cue.sfx).map((effect) => (
        <Sequence key={`${effect.file}-${effect.frame}`} from={effect.frame} layout="none">
          <Audio src={staticFile(effect.file)} volume={effect.volume ?? 0.7} />
        </Sequence>
      ))}
    </>
  );
};
