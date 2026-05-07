import React from 'react';
import {
  AbsoluteFill,
  Img,
  Sequence,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from 'remotion';

export type Shot = {
  image: string;
  narration: string;
  durationSeconds: number;
};

export type EpisodeProps = {
  title: string;
  shots: Shot[];
};

const TRANSITION_FRAMES = 18;

export const EpisodeComposition: React.FC<EpisodeProps> = ({ shots }) => {
  const { fps } = useVideoConfig();

  let cursor = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: 'black' }}>
      {shots.map((shot, idx) => {
        const duration = Math.round(shot.durationSeconds * fps);
        const from = cursor;
        cursor += duration;
        return (
          <Sequence
            key={idx}
            from={from}
            durationInFrames={duration + TRANSITION_FRAMES}
          >
            <ShotView shot={shot} duration={duration} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

const ShotView: React.FC<{ shot: Shot; duration: number }> = ({
  shot,
  duration,
}) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const opacity = interpolate(
    frame,
    [0, TRANSITION_FRAMES, duration, duration + TRANSITION_FRAMES],
    [0, 1, 1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  const zoom = interpolate(frame, [0, duration + TRANSITION_FRAMES], [1, 1.06], {
    extrapolateRight: 'clamp',
  });

  const subtitleOpacity = interpolate(
    frame,
    [TRANSITION_FRAMES, TRANSITION_FRAMES + 12],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  const subtitleY = interpolate(
    frame,
    [TRANSITION_FRAMES, TRANSITION_FRAMES + 18],
    [40, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  const isVertical = height > width;

  return (
    <AbsoluteFill style={{ opacity }}>
      <AbsoluteFill style={{ transform: `scale(${zoom})` }}>
        <Img
          src={staticFile(shot.image)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
          }}
        />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          background:
            'linear-gradient(to top, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0) 35%)',
        }}
      />
      <AbsoluteFill
        style={{
          justifyContent: 'flex-end',
          alignItems: 'center',
          paddingBottom: isVertical ? 180 : 80,
          paddingLeft: 60,
          paddingRight: 60,
        }}
      >
        <div
          style={{
            opacity: subtitleOpacity,
            transform: `translateY(${subtitleY}px)`,
            color: 'white',
            fontFamily: 'system-ui, -apple-system, sans-serif',
            fontSize: isVertical ? 48 : 44,
            fontWeight: 600,
            lineHeight: 1.3,
            textAlign: 'center',
            textShadow: '0 2px 8px rgba(0,0,0,0.6)',
            maxWidth: isVertical ? 900 : 1500,
          }}
        >
          {shot.narration}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
