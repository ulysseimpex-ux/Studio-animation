import React from 'react';
import { Composition, staticFile } from 'remotion';
import { EpisodeComposition, EpisodeProps } from './Episode';
import propsJson from '../props.json';

const FPS = 30;

const props = propsJson as EpisodeProps;

const totalFrames = props.shots.reduce(
  (acc, shot) => acc + Math.round(shot.durationSeconds * FPS),
  0
);

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="EpisodeHorizontal"
        component={EpisodeComposition}
        durationInFrames={Math.max(totalFrames, FPS)}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={props}
      />
      <Composition
        id="EpisodeVertical"
        component={EpisodeComposition}
        durationInFrames={Math.max(totalFrames, FPS)}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={props}
      />
    </>
  );
};

export { staticFile };
