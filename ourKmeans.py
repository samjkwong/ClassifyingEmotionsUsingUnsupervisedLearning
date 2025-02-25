import sys
from time import time
from collections import defaultdict
import numpy as np
import scipy
import matplotlib.pyplot as plt
from skimage import io, feature, color
import random
import pprint as pp
from tempfile import TemporaryFile

def kmeans(examples, K, maxIters, sz):
    '''
    examples: list of examples, each example is a string-to-double dict representing a sparse vector.
    K: number of desired clusters. Assume that 0 < K <= |examples|.
    maxIters: maximum number of iterations to run (you should terminate early if the algorithm converges).
    Return: (length K list of cluster centroids,
            list of assignments (i.e. if examples[i] belongs to centers[j], then assignments[i] = j)
            final reconstruction loss)
    '''
    # BEGIN_YOUR_CODE (our solution is 32 lines of code, but don't worry if you deviate from this)
    centers, assignments = [examples[i] for i in sorted(random.sample(range(0, len(examples)), K))], {}
    prev_rec_loss, rec_loss = -1, 0

    # ||u-x_i||^2=uTu-2uTx_i +x_iTx_i
    # Precalculate x_iTx_i portion, only need to do this once
    xTx = []
    for i in range(0, len(examples)):
        xTx.append(np.dot(examples[i], examples[i]))

    while maxIters > 0:
        # Precalculate uTu portion, only need to do this once per iteration
        uTu = []
        for j in range(0, K):
            uTu.append(np.dot(centers[j], centers[j]))

        # Assign
        rec_loss = 0
        new_centers = []
        for j in range(0, K):
            new_centers.append([0, np.zeros(sz)])
        for i in range(0, len(examples)):
            rec_losses = []
            for j in range(0, K):
                uTx_i = np.dot(centers[j], examples[i])
                rec_losses.append((uTu[j] - 2 * uTx_i + xTx[i], j))
            min_loss, ind = min(rec_losses)
            rec_loss += min_loss
            assignments[i] = ind
            N, sum_vec = new_centers[ind]
            sum_vec_new = sum_vec + examples[i]
            new_centers[ind] = (N + 1, sum_vec_new)

        # Recalculate
        for j in range(0, K):
            N, new_center = new_centers[j]
            scale = 1 / float(N) if N > 0 else 0
            new_center = np.multiply(new_center, scale)
            centers[j] = new_center
        if rec_loss == prev_rec_loss:
            print("Converged at " + str(rec_loss))
            break
        print("Reconstruction Loss at Iter #" + str(maxIters) + " = " + str(rec_loss))
        prev_rec_loss = rec_loss
        maxIters -= 1
    return centers, assignments, rec_loss


def kmeans_fast(features, k, num_iters=100):
    """ Use kmeans algorithm to group features into k clusters.

    This function makes use of numpy functions and broadcasting to speed up the
    first part(cluster assignment) of kmeans algorithm.

    Hints
    - You may find np.repeat and np.argmin useful

    Args:
        features - Array of N features vectors. Each row represents a feature
            vector.
        k - Number of clusters to form.
        num_iters - Maximum number of iterations the algorithm will run.

    Returns:
        assignments - Array representing cluster assignment of each point.
            (e.g. i-th point is assigned to cluster assignments[i])
    """
    N = len(features)
    print(N)
    # Randomly initalize cluster centers
    centers, assignments = np.array([features[i] for i in sorted(random.sample(range(0, len(features)), K))]), {}
    _, dim = centers.shape

    tile_f = np.tile(features, (k, 1))
    for n in range(num_iters):
        tile_c = np.repeat(centers, N, axis=0)
        tile_sub = np.subtract(tile_f, tile_c)
        dist = np.linalg.norm(tile_sub, axis=1).reshape(k, N)
        assignments_new = np.argmin(dist, axis=0)
        if np.array_equal(assignments, assignments_new):
            break
        else:
            assignments = assignments_new

        old_centers, new_stats = centers[:], []
        for j in range(0, k):
            new_stats.append([0, []])
        for i in range(len(features)):
            c_ind = int(assignments[i])
            num, sum_vec = new_stats[c_ind]
            sum_vec_new = np.add(sum_vec, features[i]) if len(sum_vec) > 0 else features[i]
            new_stats[c_ind] = [num + 1, sum_vec_new]

        new_centers = np.zeros((k, dim))
        for j in range(0, k):
            num, new_center = new_stats[j]
            new_center = np.divide(new_center, num)
            new_centers[j] = np.array(new_center)
        centers = new_centers

    return centers, assignments, 0