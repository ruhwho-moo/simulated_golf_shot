# GSPro Percent Shot Carry Reference
This printout uses your stock carry yardages and the script's percentage-distance formula:
```python
distance_scale = (percent / 100) ** 1.15
estimated_carry = stock_carry * distance_scale
```
These are estimated **carry** numbers before random variance, mishits, launch/spin effects, rollout, wind, elevation, lie, and GSPro course physics.
Putter is not included because putter commands use **feet**, not percentage.

## Reference Table
| Club | Stock | 25% | 30% | 40% | 50% | 60% | 70% | 75% | 80% | 85% | 90% | 95% | 100% | 105% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Driver | 265 | 53.8 | 66.4 | 92.4 | 119.4 | 147.3 | 175.8 | 190.4 | 205.0 | 219.8 | 234.8 | 249.8 | 265.0 | 280.3 |
| 3 Wood | 235 | 47.7 | 58.9 | 81.9 | 105.9 | 130.6 | 155.9 | 168.8 | 181.8 | 194.9 | 208.2 | 221.5 | 235.0 | 248.6 |
| 4 Hybrid | 215 | 43.7 | 53.8 | 75.0 | 96.9 | 119.5 | 142.7 | 154.4 | 166.3 | 178.3 | 190.5 | 202.7 | 215.0 | 227.4 |
| 5 Iron | 195 | 39.6 | 48.8 | 68.0 | 87.9 | 108.4 | 129.4 | 140.1 | 150.9 | 161.8 | 172.7 | 183.8 | 195.0 | 206.3 |
| 6 Iron | 185 | 37.6 | 46.3 | 64.5 | 83.4 | 102.8 | 122.8 | 132.9 | 143.1 | 153.5 | 163.9 | 174.4 | 185.0 | 195.7 |
| 7 Iron | 175 | 35.5 | 43.8 | 61.0 | 78.9 | 97.3 | 116.1 | 125.7 | 135.4 | 145.2 | 155.0 | 165.0 | 175.0 | 185.1 |
| 8 Iron | 160 | 32.5 | 40.1 | 55.8 | 72.1 | 88.9 | 106.2 | 114.9 | 123.8 | 132.7 | 141.7 | 150.8 | 160.0 | 169.2 |
| 9 Iron | 150 | 30.5 | 37.6 | 52.3 | 67.6 | 83.4 | 99.5 | 107.7 | 116.0 | 124.4 | 132.9 | 141.4 | 150.0 | 158.7 |
| Pitching Wedge | 135 | 27.4 | 33.8 | 47.1 | 60.8 | 75.0 | 89.6 | 97.0 | 104.4 | 112.0 | 119.6 | 127.3 | 135.0 | 142.8 |
| 48 Degree Wedge | 120 | 24.4 | 30.1 | 41.8 | 54.1 | 66.7 | 79.6 | 86.2 | 92.8 | 99.5 | 106.3 | 113.1 | 120.0 | 126.9 |
| Gap Wedge | 110 | 22.3 | 27.5 | 38.3 | 49.6 | 61.1 | 73.0 | 79.0 | 85.1 | 91.2 | 97.4 | 103.7 | 110.0 | 116.3 |
| Sand Wedge | 95 | 19.3 | 23.8 | 33.1 | 42.8 | 52.8 | 63.0 | 68.2 | 73.5 | 78.8 | 84.2 | 89.6 | 95.0 | 100.5 |
| Lob Wedge | 85 | 17.3 | 21.3 | 29.6 | 38.3 | 47.2 | 56.4 | 61.1 | 65.8 | 70.5 | 75.3 | 80.1 | 85.0 | 89.9 |

## Example Commands
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
putt 12
putt 35
```

## How to read the table
- `7i 100` is based on your 175-yard stock 7 iron.
- `7i 85` is estimated around the 85% carry value in the table, then the script adds natural variance.
- `sw 50` is based on your 95-yard sand wedge and plays like a partial pitch-style shot.
- `lw 30` is based on your 85-yard lob wedge and plays more like a chip-style shot.
- `putt 12` means a 12-foot putt, not 12%.
