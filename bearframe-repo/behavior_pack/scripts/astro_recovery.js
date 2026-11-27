// Only accept an occupied section if every cell matches the packaged structure.
export function matchesAstroSection(dim, origin, size, structure) {
  if (!structure) return false;
  const [width, height, depth] = size;
  for (let x = 0; x < width; x++) {
    for (let y = 0; y < height; y++) {
      for (let z = 0; z < depth; z++) {
        const local = {x, y, z};
        const expected = structure.getBlockPermutation(local);
        const actual = dim.getBlock({x: origin.x + x, y: origin.y + y, z: origin.z + z});
        if (!actual) return false;
        if (!expected) {
          if (!actual.isAir) return false;
          continue;
        }
        if (!actual.permutation.matches(expected.type.id, expected.getAllStates()) ||
            actual.isWaterlogged !== structure.getIsWaterlogged(local)) return false;
      }
    }
  }
  return true;
}
