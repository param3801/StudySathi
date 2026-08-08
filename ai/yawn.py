from scipy.spatial import distance

# Mouth landmarks
MOUTH = [61, 13, 291, 14]


def calculate_mar(landmarks, width, height):

    points = []

    for idx in MOUTH:

        lm = landmarks[idx]

        x = int(lm.x * width)
        y = int(lm.y * height)

        points.append((x, y))

    left, top, right, bottom = points

    vertical = distance.euclidean(top, bottom)
    horizontal = distance.euclidean(left, right)

    mar = vertical / horizontal

    return mar