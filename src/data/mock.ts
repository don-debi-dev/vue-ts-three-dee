  export const colors = [
  {
    "color": "#ff0000",
    "tag": "red"
  },
  {
    "color": "#00ff00",
    "tag": "green"
  },
  {
    "color": "#0000ff",
    "tag": "blue"
  }
];

export const shape = {
  "radius": 0.5,
  "widthSegments": 32,
  "heightSegments": 32,
}

export type DataType = {
  position: { 
    x: number, 
    y: number, 
    z: number, 
  }; 
  color: string, 
  tag: string, 
  radius: number, 
  widthSegments: number, 
  heightSegments: number
}