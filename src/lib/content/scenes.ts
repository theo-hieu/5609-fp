import type { SceneCopy } from '$lib/types';

export const scenes: SceneCopy[] = [
  {
    id: 1,
    eyebrow: 'Scene 1',
    title: 'The Value of Distance',
    description:
      'The shot chart starts with a simple truth: distance hurts accuracy, but the 3-point line changes the reward.',
    paragraphs: [
      'Every extra step away from the rim makes the shot a little harder. Finishes in the paint are converted at the highest rates, then efficiency steadily slides as attempts move through the lane, into the floater area, and out toward the long two.',
      'The twist is that the court does not pay every made basket the same way. Once a shooter crosses the 3-point line, the expected value of the attempt jumps from two points to three, and that extra point can outweigh the drop in raw field goal percentage.',
      'That is why the distance profile bends around the arc. Shots from 22 feet and beyond are less accurate than short jumpers, but they can still return more points per attempt, which makes them rational shots for modern offenses to keep hunting.'
    ]
  },
  {
    id: 2,
    eyebrow: 'Scene 2',
    title: 'Hunting High-Value Real Estate',
    description:
      'Once teams understand the math, shot selection stops looking balanced and starts looking optimized.',
    paragraphs: [
      'If the rim produces the easiest two points and the arc produces the most valuable jumpers, offenses naturally stop treating the court as evenly useful space. The result is a map with two bright clusters instead of one smooth spread of attempts.',
      'The heatmap shows those two magnets clearly: a dense pocket directly at the basket and a ring of attempts sitting just behind the 3-point line. Those are the places where expected return is strongest, so that is where possessions get concentrated.',
      'Everything in between pays the price. Mid-range shots never disappear completely, but compared with the paint and the arc, that part of the floor becomes noticeably quiet because it offers neither elite accuracy nor elite scoring value.'
    ]
  },
  {
    id: 3,
    eyebrow: 'Scene 3',
    title: 'Court Geography & Zones',
    description:
      'Distance alone is not enough. The shape of the line itself creates some of the most efficient shots on the floor.',
    paragraphs: [
      'Not all threes are created equal. The corner 3 is closer to the basket than an above-the-break 3, yet it is still worth the same three points, which means the geometry of the court creates a special shortcut to efficient offense.',
      'That shorter path makes the corner three one of the best non-rim shots in basketball. Outside of dunks, layups, and point-blank finishes, it is often the cleanest combination of manageable distance and maximum reward.',
      "When the view switches to made shots, the most productive zones sharpen immediately. The paint glows because close finishes are efficient, and the corners stand out because spacing the floor there turns court geometry into one of the league's most reliable sources of efficient scoring."
    ]
  }
];
