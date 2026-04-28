export type Definition = {
  key: string;
  label: string;
  definition: string;
};

export const definitions: Definition[] = [
  {
    key: 'three_point_line',
    label: 'Three-point line',
    definition:
      'The arc on the basketball court beyond which a successful field goal is worth three points instead of two.'
  },
  {
    key: 'rim',
    label: 'Rim',
    definition: 'The hoop area close to the basket; shots here tend to have the highest conversion rates.'
  },
  {
    key: 'midrange',
    label: 'Mid-range',
    definition:
      'The area inside the three-point arc but away from the rim; historically common but less favored in modern offenses.'
  },
  {
    key: 'field_goal_percentage',
    label: 'Field goal percentage',
    definition: 'The ratio of made shots to attempted shots, expressed as a percentage.'
  },
  {
    key: 'attempts',
    label: 'Attempts',
    definition: 'The total number of shot attempts from a location or player.'
  }
];
