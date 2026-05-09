# GSPro Percent-Based Shot Generator README

## Purpose

This script lets you send simulated golf shots into GSPro Open Connect using your stock carry yardages. It is useful for testing a GSPro course, landing zones, green behavior, hazards, routing, and shot reactions without needing to physically hit every shot.

It supports:

- Full and partial shots by club percentage
- Random draw/fade/straight variance
- Occasional mishits
- Wedge partial-shot behavior
- Putter commands by feet
- Your personal stock carry yardages

## Your Stock Carry Yardages

| Club Key | Club | Stock Carry |
|---|---:|---:|
| `driver` | Driver | 265 yards |
| `3w` | 3 Wood | 235 yards |
| `4h` | 4 Hybrid | 215 yards |
| `5i` | 5 Iron | 195 yards |
| `6i` | 6 Iron | 185 yards |
| `7i` | 7 Iron | 175 yards |
| `8i` | 8 Iron | 160 yards |
| `9i` | 9 Iron | 150 yards |
| `pw` | Pitching Wedge | 135 yards |
| `48` | 48 Degree Wedge | 120 yards |
| `gw` | Gap Wedge | 110 yards |
| `sw` | Sand Wedge | 95 yards |
| `lw` | Lob Wedge | 85 yards |

## Command Format

For every club except putter:

```text
club percent
```

Examples:

```text
driver 100
driver 80
3w 90
4h 100
7i 85
pw 75
48 50
gw 60
sw 50
lw 30
```

For putter:

```text
putt feet
```

Examples:

```text
putt 5
putt 12
putt 35
```

Important: `putt 12` means a 12-foot putt. It does not mean 12%.

## GSPro Setup

1. Open GSPro.
2. Open GSPro Connect / Open Connect.
3. Make sure it is listening locally.
4. Run the Python script.
5. Enter commands in the console.

The script is designed to send data to:

```text
127.0.0.1:0921
```

## How Percentage Shots Work

The script uses a non-linear carry-distance formula:

```python
distance_scale = (percent / 100) ** 1.15
estimated_carry = stock_carry * distance_scale
```

This means a 50% swing does not fly exactly 50% of your full carry. Partial shots are intentionally modeled to lose more carry, especially with wedges.

Examples using your stock numbers:

- `driver 100` starts around 265 carry
- `driver 80` starts around 205 carry
- `7i 100` starts around 175 carry
- `7i 85` starts around 145 carry
- `sw 50` starts around 43 carry
- `lw 30` starts around 21 carry

The exact shot will still vary because the script adds randomness.

## Random Variance

Each shot gets random variation in:

- Ball speed
- Launch angle
- Spin
- Start direction
- Spin axis
- Carry estimate
- Shot shape

The script can produce:

- Draw
- Fade
- Straight-ish shot
- Pull hook
- Push slice
- Mishit
- Chunked wedge
- Bladed wedge
- Pace miss on putts

## Wedge Behavior

For wedges, the script changes behavior based on swing percentage:

| Percent | Shot Type |
|---:|---|
| 10–35% | Chip-style |
| 36–60% | Pitch-style |
| 61–85% | Partial wedge |
| 86–115% | Full-ish wedge |

Wedge clubs:

```text
pw
48
gw
sw
lw
```

## Putter Behavior

Putter commands use feet:

```text
putt 10
```

The script converts that to a rough GSPro ball speed and adds pace/start-line variance.

The putting speed formula is:

```python
speed = 2.2 + intended_feet * 0.18
```

If putts go too far in GSPro, lower `0.18`.
If putts come up short, raise `0.18`.

Suggested tuning range:

```python
0.15 to 0.22
```

## Useful Test Sessions

### Tee Shot Testing

```text
driver 100
driver 90
driver 80
3w 100
3w 90
4h 100
```

### Approach Testing

```text
5i 100
6i 100
7i 100
8i 100
9i 100
pw 100
```

### Partial Wedge Testing

```text
pw 75
48 75
gw 60
sw 50
lw 30
```

### Putting Green Testing

```text
putt 5
putt 10
putt 20
putt 40
putt 60
```

## Tuning Partial Shot Distance

Find this part in the script:

```python
speed_scale = pct ** 0.82
distance_scale = pct ** 1.15
```

If partial shots go too far, change:

```python
distance_scale = pct ** 1.25
```

If partial shots come up too short, change:

```python
distance_scale = pct ** 1.05
```

## Tuning Shot Shape Direction

If GSPro shows draws and fades backward, flip the sign of spin axis where the shot shape is generated.

Current assumption for a right-handed golfer:

```text
negative spin axis = draw/hook
positive spin axis = fade/slice
```

## Important Limitations

This is not a replacement for a real launch monitor. It is best used for testing:

- Course playability
- Landing zones
- Greens
- Hazards
- Terrain
- Shot reactions
- Routing
- Simulator camera behavior

It should not be used to validate your real swing or your launch monitor accuracy.

## Recommended Workflow

1. Start with `driver 100` to test tee-shot landing.
2. Use `7i 100`, `9i 100`, and `pw 100` to test common approach shots.
3. Use `sw 50`, `lw 30`, and `48 75` to test short-game behavior.
4. Use `putt 5`, `putt 20`, and `putt 40` to test green speeds and slopes.
5. Adjust the formula if GSPro behavior feels too long or too short.
