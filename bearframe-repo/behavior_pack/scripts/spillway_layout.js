export const SPILLWAY_MARKER = "bearframe:spillway_datum";
export const SPILLWAY_BUILT = "bearframe:excavated";
export const SPILLWAY_SIZE = {x: 69, y: 28, z: 37};
export const SPILLWAY_DATUM = [2, 20, 18];
export const SPILLWAY_PANEL = [37, 5, 18];

// Inclusive outer rectangle and roof height for each below-grade room.
export const SPILLWAY_ROOMS = [
  {id: "landing", rect: [22, 14, 29, 22], roof: 10},
  {id: "concourse", rect: [28, 13, 49, 23], roof: 11},
  {id: "pump", rect: [27, 2, 47, 13], roof: 13},
  {id: "operations", rect: [28, 23, 39, 34], roof: 10},
  {id: "workshop", rect: [39, 23, 49, 34], roof: 10},
];

export const SPILLWAY_FLIGHT = Array.from({length: 18}, (_, i) => ({
  x: i + 4,
  y: i < 8 ? 19 - i : i < 11 ? 11 : 21 - i,
  stair: i < 8 || i >= 11,
}));

export const SPILLWAY_SIGNS = [
  {pos:[1,21,15],rotation:4,text:"SPILLWAY 04\nWaterworks access\nLower gallery"},
  {pos:[26,5,15],rotation:12,text:"SERVICE LEVEL\nPump hall: north\nOps / workshop: south"},
  {pos:[31,5,11],rotation:8,text:"PUMP HALL\nIntake offline\nKeep to dry rim"},
  {pos:[34,5,27],rotation:8,text:"SHIFT RECORD\nIntake 2 lost pressure.\nIsolated the bypass.\nNight crew evacuated."},
  {pos:[43,5,26],rotation:8,text:"MAINTENANCE\nHoist / spares\nLockout in effect"},
  {pos:[38,5,17],rotation:8,text:"AUXILIARY PUMP\n2 redstone to restore\nStores interlock"},
];
