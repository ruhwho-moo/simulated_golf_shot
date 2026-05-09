import socket
import json
import random
import time
from dataclasses import dataclass

GS_PRO_HOST = "127.0.0.1"
GS_PRO_PORT = 921


@dataclass
class ClubProfile:
    name: str
    code: str
    ball_speed: float
    launch: float
    spin: float
    carry: float
    hla_std: float
    launch_std: float
    speed_std: float
    spin_std: float
    spin_axis_std: float


CLUBS = {
    "driver": ClubProfile("Driver", "DR", 150, 13.0, 2600, 265, 3.0, 1.8, 5.5, 500, 8.0),
    "3w": ClubProfile("3 Wood", "3W", 138, 12.5, 3400, 235, 2.8, 1.7, 4.5, 550, 7.0),
    "4h": ClubProfile("4 Hybrid", "4H", 128, 15.0, 4300, 215, 2.5, 1.6, 3.8, 550, 6.0),

    "5i": ClubProfile("5 Iron", "5I", 119, 14.0, 5000, 195, 2.3, 1.4, 3.2, 500, 5.0),
    "6i": ClubProfile("6 Iron", "6I", 113, 15.5, 5700, 185, 2.1, 1.3, 3.0, 475, 4.8),
    "7i": ClubProfile("7 Iron", "7I", 107, 17.0, 6500, 175, 2.0, 1.2, 2.8, 450, 4.5),
    "8i": ClubProfile("8 Iron", "8I", 99, 19.0, 7400, 160, 1.8, 1.2, 2.5, 425, 4.2),
    "9i": ClubProfile("9 Iron", "9I", 93, 21.0, 8300, 150, 1.7, 1.1, 2.3, 400, 4.0),

    "pw": ClubProfile("Pitching Wedge", "PW", 86, 24.0, 9300, 135, 1.5, 1.0, 2.0, 400, 3.8),
    "48": ClubProfile("48 Degree Wedge", "48", 80, 26.0, 9500, 120, 1.4, 1.0, 1.8, 375, 3.6),
    "gw": ClubProfile("Gap Wedge", "GW", 76, 28.0, 9800, 110, 1.4, 1.0, 1.8, 375, 3.5),
    "sw": ClubProfile("Sand Wedge", "SW", 69, 31.0, 10000, 95, 1.3, 1.0, 1.6, 350, 3.2),
    "lw": ClubProfile("Lob Wedge", "LW", 62, 34.0, 10500, 85, 1.3, 1.1, 1.5, 350, 3.0),

    "putter": ClubProfile("Putter", "PT", 8, 1.0, 100, 10, 0.8, 0.2, 1.0, 25, 0.5),
}

shot_number = 1


def clamp(value, low, high):
    return max(low, min(high, value))


def feet_to_yards(feet):
    return feet / 3.0


def choose_shot_shape(percent):
    """
    For a right-handed golfer:
      negative spin axis = draw/hook tendency
      positive spin axis = fade/slice tendency

    Lower-effort shots are usually straighter, so variance tightens as percent drops.
    """

    if percent < 60:
        roll = random.random()
        if roll < 0.45:
            return "small draw", random.uniform(-4, -1)
        elif roll < 0.90:
            return "small fade", random.uniform(1, 4)
        else:
            return "straight-ish", random.uniform(-1, 1)

    roll = random.random()

    if roll < 0.32:
        return "draw", random.uniform(-8, -2)
    elif roll < 0.64:
        return "fade", random.uniform(2, 8)
    elif roll < 0.84:
        return "straight-ish", random.uniform(-2, 2)
    elif roll < 0.92:
        return "pull hook", random.uniform(-18, -9)
    else:
        return "push slice", random.uniform(9, 18)


def percent_to_power(percent):
    """
    Converts a stated swing percentage into a usable power scale.

    This is intentionally not linear.
    A 50% wedge does not usually fly exactly half as far with exactly half ball speed.
    """

    pct = clamp(percent, 10, 115) / 100.0

    # Ball speed scale. Softer swings lose speed, but not always perfectly linear.
    speed_scale = pct ** 0.82

    # Carry/distance scale. Distance drops more than ball speed on partial shots.
    distance_scale = pct ** 1.15

    return speed_scale, distance_scale


def generate_percent_shot(club_key, percent):
    club = CLUBS[club_key]
    percent = clamp(float(percent), 10, 115)

    speed_scale, distance_scale = percent_to_power(percent)

    shape, spin_axis_bias = choose_shot_shape(percent)

    is_wedge = club_key in ["pw", "gw", "sw", "lw"]
    is_driver_or_wood = club_key in ["driver", "3w", "5w"]

    speed = club.ball_speed * speed_scale
    carry = club.carry * distance_scale

    # Launch adjustments:
    # Partial wedges tend to launch lower on chips/knockdowns unless you open the face.
    # Partial woods/driver are more like controlled tee shots.
    if is_wedge:
        if percent <= 35:
            launch_adjust = -12
            spin_scale = 0.45
            shot_type = "chip-style"
        elif percent <= 60:
            launch_adjust = -7
            spin_scale = 0.65
            shot_type = "pitch-style"
        elif percent <= 85:
            launch_adjust = -3
            spin_scale = 0.85
            shot_type = "partial"
        else:
            launch_adjust = 0
            spin_scale = 1.00
            shot_type = "full-ish"
    elif is_driver_or_wood:
        if percent < 75:
            launch_adjust = -2
            spin_scale = 0.90
            shot_type = "controlled"
        else:
            launch_adjust = 0
            spin_scale = 1.00
            shot_type = "full"
    else:
        if percent < 75:
            launch_adjust = -3
            spin_scale = 0.88
            shot_type = "knockdown"
        else:
            launch_adjust = 0
            spin_scale = 1.00
            shot_type = "full"

    speed = random.gauss(speed, club.speed_std * max(0.45, percent / 100))
    launch = random.gauss(club.launch + launch_adjust, club.launch_std)
    spin = random.gauss(club.spin * spin_scale, club.spin_std * max(0.50, percent / 100))

    # Lower effort = tighter directional spread.
    direction_scale = clamp(percent / 100, 0.45, 1.10)
    hla = random.gauss(0, club.hla_std * direction_scale)
    spin_axis = spin_axis_bias + random.gauss(0, (club.spin_axis_std / 2) * direction_scale)

    # Random mishits.
    # Partial wedge shots can be chunked/bladed.
    mishit_chance = 0.08 if percent >= 75 else 0.11
    big_miss_chance = 0.04 if percent >= 75 else 0.02

    miss_label = ""

    if random.random() < mishit_chance:
        if is_wedge and percent <= 65:
            if random.random() < 0.55:
                # chunk
                speed *= random.uniform(0.60, 0.82)
                carry *= random.uniform(0.55, 0.80)
                launch -= random.uniform(2, 7)
                spin *= random.uniform(0.55, 0.85)
                miss_label = " chunked"
            else:
                # blade
                speed *= random.uniform(1.10, 1.35)
                carry *= random.uniform(1.20, 1.60)
                launch -= random.uniform(6, 14)
                spin *= random.uniform(0.40, 0.75)
                miss_label = " bladed"
        else:
            speed *= random.uniform(0.88, 0.96)
            carry *= random.uniform(0.88, 0.97)
            hla += random.choice([-1, 1]) * random.uniform(2.0, 5.0)
            spin_axis += random.choice([-1, 1]) * random.uniform(4.0, 10.0)
            miss_label = " mishit"

    if random.random() < big_miss_chance:
        hla += random.choice([-1, 1]) * random.uniform(5.0, 10.0)
        spin_axis += random.choice([-1, 1]) * random.uniform(10.0, 22.0)
        carry *= random.uniform(0.85, 1.05)
        miss_label += " BIG MISS"

    speed = clamp(speed, 3, club.ball_speed * 1.15)
    launch = clamp(launch, 2, 45)
    spin = clamp(spin, 500, 12000)
    hla = clamp(hla, -15, 15)
    spin_axis = clamp(spin_axis, -35, 35)
    carry = clamp(carry, 1, club.carry * 1.15)

    return {
        "shape": f"{club.name} {percent:.0f}% {shot_type} {shape}{miss_label}",
        "ball_data": {
            "Speed": round(speed, 1),
            "SpinAxis": round(spin_axis, 1),
            "TotalSpin": round(spin, 0),
            "HLA": round(hla, 1),
            "VLA": round(launch, 1),
            "CarryDistance": round(carry, 1),
            "TotalDistance": round(carry * random.uniform(1.00, 1.12), 1),
        }
    }


def generate_putt_distance_shot(target_feet):
    target_feet = clamp(float(target_feet), 1, 120)

    if target_feet <= 5:
        distance_error_feet = random.uniform(-0.5, 0.6)
    elif target_feet <= 15:
        distance_error_feet = random.uniform(-1.2, 1.5)
    elif target_feet <= 35:
        distance_error_feet = random.uniform(-2.5, 3.5)
    else:
        distance_error_feet = random.uniform(-5.0, 7.0)

    intended_feet = max(1, target_feet + distance_error_feet)

    # Tune this if GSPro putts are too long/short.
    speed = 2.2 + intended_feet * 0.18

    label_suffix = ""

    if random.random() < 0.05:
        speed *= random.uniform(0.65, 0.82)
        intended_feet *= random.uniform(0.65, 0.82)
        label_suffix = " left short"
    elif random.random() < 0.05:
        speed *= random.uniform(1.18, 1.38)
        intended_feet *= random.uniform(1.18, 1.38)
        label_suffix = " ran by"

    if target_feet <= 8:
        hla = random.gauss(0, 0.45)
    elif target_feet <= 25:
        hla = random.gauss(0, 0.75)
    else:
        hla = random.gauss(0, 1.1)

    speed = clamp(speed, 1.0, 24.0)
    hla = clamp(hla, -4, 4)

    return {
        "shape": f"Putt to {target_feet:.1f} feet{label_suffix}",
        "ball_data": {
            "Speed": round(speed, 1),
            "SpinAxis": 0.0,
            "TotalSpin": 50,
            "HLA": round(hla, 1),
            "VLA": 0.5,
            "CarryDistance": round(feet_to_yards(intended_feet), 2),
            "TotalDistance": round(feet_to_yards(intended_feet), 2),
        }
    }


def build_payload_from_ball_data(ball_data):
    global shot_number

    payload = {
        "DeviceID": "Python Percent Shot Tester",
        "Units": "Yards",
        "ShotNumber": shot_number,
        "APIversion": "1",
        "BallData": ball_data,
        "ClubData": {
            "Speed": 0.0,
            "AngleOfAttack": 0.0,
            "FaceToTarget": 0.0,
            "Lie": 0.0,
            "Loft": 0.0,
            "Path": 0.0,
            "SpeedAtImpact": 0.0,
            "VerticalFaceImpact": 0.0,
            "HorizontalFaceImpact": 0.0,
            "ClosureRate": 0.0
        },
        "ShotDataOptions": {
            "ContainsBallData": True,
            "ContainsClubData": False,
            "LaunchMonitorIsReady": True,
            "LaunchMonitorBallDetected": True,
            "IsHeartBeat": False
        }
    }

    shot_number += 1
    return payload


def send_to_gspro(payload):
    message = json.dumps(payload)

    with socket.create_connection((GS_PRO_HOST, GS_PRO_PORT), timeout=5) as sock:
        sock.sendall(message.encode("utf-8"))

        try:
            sock.settimeout(2)
            response = sock.recv(4096)
            return response.decode("utf-8", errors="ignore")
        except socket.timeout:
            return "No response received."


def send_payload(payload, description):
    print("\nSending shot to GSPro...")
    print(f"Shot: {description}")
    print(json.dumps(payload["BallData"], indent=2))

    try:
        response = send_to_gspro(payload)
        print("GSPro response:")
        print(response)
    except ConnectionRefusedError:
        print("\nERROR: Could not connect to GSPro.")
        print("Make sure GSPro Connect is open and listening on 127.0.0.1:0921.")
    except Exception as e:
        print(f"\nERROR: {e}")


def hit_percent_shot(club_key, percent):
    if club_key not in CLUBS or club_key == "putter":
        print("Use a real club key like driver, 7i, sw, lw. For putter use: putt 10")
        return

    shot = generate_percent_shot(club_key, percent)
    payload = build_payload_from_ball_data(shot["ball_data"])
    send_payload(payload, shot["shape"])


def hit_putt_distance(target_feet):
    shot = generate_putt_distance_shot(target_feet)
    payload = build_payload_from_ball_data(shot["ball_data"])
    send_payload(payload, shot["shape"])


def list_clubs():
    print("\nAvailable clubs:")
    for key, club in CLUBS.items():
        if key != "putter":
            print(f"  {key:8} - {club.name}")

    print("\nExamples:")
    print("  driver 100")
    print("  driver 80")
    print("  7i 100")
    print("  7i 75")
    print("  sw 50")
    print("  lw 30")
    print("  pw 85")
    print("  putt 10")


def random_bag_session(number_of_shots=14, delay_seconds=4):
    keys = [k for k in CLUBS.keys() if k != "putter"]

    for _ in range(number_of_shots):
        club_key = random.choice(keys)
        percent = random.choice([65, 75, 85, 90, 100])
        hit_percent_shot(club_key, percent)
        time.sleep(delay_seconds)


def random_short_game_session(number_of_shots=10, delay_seconds=4):
    for _ in range(number_of_shots):
        if random.random() < 0.70:
            club_key = random.choice(["pw", "gw", "sw", "lw"])
            percent = random.choice([20, 25, 30, 40, 50, 60, 70, 80])
            hit_percent_shot(club_key, percent)
        else:
            feet = random.choice([3, 5, 8, 10, 15, 20, 30, 40, 60])
            hit_putt_distance(feet)

        time.sleep(delay_seconds)


def play_menu():
    print("GSPro Percent-Based Shot Generator")
    print("----------------------------------")
    print("Start GSPro, open GSPro Connect, then use this script.")
    print("Format: club percent")
    print("Putter format: putt feet")

    list_clubs()

    while True:
        print("\nOptions:")
        print("  driver 100       = full driver")
        print("  driver 80        = controlled driver")
        print("  7i 90            = 90% 7 iron")
        print("  sw 50            = 50% sand wedge")
        print("  lw 30            = 30% lob wedge")
        print("  putt 12          = putt 12 feet")
        print("  random           = one random non-putter shot")
        print("  bag              = 14 random non-putter shots")
        print("  short            = random wedge/putt session")
        print("  list             = list clubs/examples")
        print("  quit             = exit")

        choice = input("\nEnter choice: ").strip().lower()
        parts = choice.split()

        if not parts:
            continue

        command = parts[0]

        if command in ["quit", "q", "exit"]:
            break

        elif command == "list":
            list_clubs()

        elif command == "random":
            club_key = random.choice([k for k in CLUBS.keys() if k != "putter"])
            percent = random.choice([65, 75, 85, 90, 100])
            hit_percent_shot(club_key, percent)

        elif command == "bag":
            random_bag_session(number_of_shots=14, delay_seconds=4)

        elif command == "short":
            random_short_game_session(number_of_shots=10, delay_seconds=4)

        elif command == "putt":
            if len(parts) != 2:
                print("Use format: putt 10")
                print("Putt distance is in feet.")
                continue

            try:
                target_feet = float(parts[1])
            except ValueError:
                print("Putt distance must be a number in feet.")
                continue

            hit_putt_distance(target_feet)

        elif command in CLUBS and command != "putter":
            if len(parts) == 1:
                # Default to 100% if you only type the club.
                hit_percent_shot(command, 100)
                continue

            if len(parts) != 2:
                print("Use format: club percent")
                print("Example: 7i 85")
                continue

            try:
                percent = float(parts[1])
            except ValueError:
                print("Percent must be a number.")
                continue

            hit_percent_shot(command, percent)

        else:
            print("Unknown choice.")


if __name__ == "__main__":
    play_menu()