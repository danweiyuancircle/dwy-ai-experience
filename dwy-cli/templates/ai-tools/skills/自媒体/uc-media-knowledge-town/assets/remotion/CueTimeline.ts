export type CueSfx = {
  file: string;
  frame: number;
  volume?: number;
};

export type Cue = {
  cueId: string;
  sceneId: string;
  startFrame: number;
  endFrame: number;
  voText: string;
  caption: {text: string; mode: 'bottomSpeechBubble'};
  visual: {action: string; keyword: string};
  sfx: CueSfx[];
};

export type CueTimeline = {
  version: 1;
  fps: number;
  voice: {file: string; timingStatus: string};
  canvas: {width: number; height: number; subtitleBandPx: number};
  cues: Cue[];
};
