import cv2
import numpy as np


class HeadPoseEstimator:

    def estimate(self, landmarks, width, height):

        face_2d = []
        face_3d = []

        indices = [33, 263, 1, 61, 291, 199]

        for idx in indices:

            lm = landmarks[idx]

            x = int(lm.x * width)
            y = int(lm.y * height)

            face_2d.append([x, y])

            face_3d.append([x, y, lm.z])

        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)

        focal_length = width

        cam_matrix = np.array([
            [focal_length, 0, width / 2],
            [0, focal_length, height / 2],
            [0, 0, 1]
        ])

        dist_matrix = np.zeros((4, 1))

        success, rot_vec, trans_vec = cv2.solvePnP(
            face_3d,
            face_2d,
            cam_matrix,
            dist_matrix
        )

        rmat, _ = cv2.Rodrigues(rot_vec)

        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

        pitch = angles[0] * 360
        yaw = angles[1] * 360

        return pitch # up and down head