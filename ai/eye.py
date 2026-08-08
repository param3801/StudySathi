from scipy.spatial import distance

LEFT_EYE = [33, 160, 158, 133, 153, 144]


def calculate_ear(landmarks, image_width, image_height):
    points = []

    for idx in LEFT_EYE:
        landmark = landmarks[idx]

        x = int(landmark.x * image_width)
        y = int(landmark.y * image_height)

        points.append((x, y))

    p1, p2, p3, p4, p5, p6 = points

    vertical1 = distance.euclidean(p2, p6)
    vertical2 = distance.euclidean(p3, p5)
    horizontal = distance.euclidean(p1, p4)

    ear = (vertical1 + vertical2) / (2.0 * horizontal)

    return ear