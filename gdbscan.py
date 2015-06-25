__author__ = 'mack0242'
import pyopencl as cl
from pyopencl.reduction import ReductionKernel
import pyopencl.array as cla
import numpy as np
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.metrics.pairwise import euclidean_distances
import math
from sklearn.preprocessing import scale
import time

class GDBSCAN(BaseEstimator, ClusterMixin):
    def __init__(self, eps, minpts, metric=None):
        self.eps = eps
        self.minpts = minpts
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)
        if metric is None:
            self.metric = lambda xs, ys: (sum([(i[0]-i[1])**2 for i in xs]))**0.5
        else:
            self.metric = metric
        source = """
            __kernel void makeGraph(__global const float2 *data,
                                    __global unsigned char *graph,
                                    const unsigned int points,
                                    const float eps) {
                int tid = get_global_id(0);
                for(size_t i = 0; i < points; i++) {
                    graph[i + points*tid] = distance(data[tid], data[i]) <= eps;
                }
            }

            __kernel void scale(__global  float2 *data,
                                const float2 mean,
                                const float2 std_dev) {
                int tid = get_global_id(0);
                data[tid] -= mean;
                data[tid] /= std_dev;
            }
            /*
            __kernel void bfs(__global const float *graph,
                             __global const float  *fa,
                             __global const float  *xa,
                             const unsigned int points) {
                int tid = get_global_id(0);
                if (fa[tid]) {
                    fa[tid] = 0;
                    xa[tid] = 1;
                    for(size_t = 0; i < points; i++) {
                        int nid = graph[tid][i];
                        if (!xa[nid]) {
                            fa[nid] = 1;
                        }
                    }
                }
            }
        */
        """
        self.graph_kernel = cl.Program(self.ctx, source).build()
        self.sum_kernel = ReductionKernel(self.ctx, cla.vec.float2,
                                     neutral="0",
                                     reduce_expr="a+b",
                                     map_expr="data[i]",
                                     arguments="__global float2 *data")
        self.std_dev_kernel = ReductionKernel(self.ctx, cla.vec.float2,
                                         neutral="0",
                                         reduce_expr="a+b",
                                         map_expr="pown(data[i]-mean,2)",
                                         arguments="__global const float2 *data, const float2 mean")

    def makeGraph(self, data):
        mf = cl.mem_flags
        data_g = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=data)
        data_g_cla = cla.Array(self.ctx, data.shape, dtype=cla.vec.float2, data=data_g)
        shape = data.shape
        size = shape[0]*shape[0]

        print "Scaling data"
        start = time.time()

        mean = self.sum_kernel(data_g_cla, queue=self.queue).get()
        mean["x"] /= shape[0]
        mean["y"] /= shape[0]

        std_dev = self.std_dev_kernel(data_g_cla, mean, queue=self.queue).get()
        std_dev["x"] = math.sqrt(std_dev["x"] / shape[0])
        std_dev["y"] = math.sqrt(std_dev["y"] / shape[0])
        # cpu_mean = sum(map(lambda x: x[0], data))/len(data), sum(map(lambda x: x[1], data))/len(data)
        # cpu_std_dev = math.sqrt(sum(map(lambda x: math.pow(x[0]-cpu_mean[0], 2), data))/len(data)), math.sqrt(sum(map(lambda x: math.pow(x[1]-cpu_mean[1], 2), data))/len(data))
        # print "gpu means=", mean
        # print "cpu means=", cpu_mean
        # print "cpu_std_dev=", cpu_std_dev
        # print "gpu_std_dev=", std_dev

        scale_event = self.graph_kernel.scale(self.queue, data.shape, None,
                                              data_g_cla.data,
                                              mean,
                                              std_dev)
        scaled_np = np.empty_like(data)
        cl.enqueue_copy(self.queue, scaled_np, data_g, wait_for=[scale_event])
        return scaled_np
        # scaled_sk = np.empty((shape[0], 2), dtype=np.float32)
        # for i in xrange(data.size):
        #     scaled_sk[i][0] = data[i][0]
        #     scaled_sk[i][1] = data[i][1]
        # scale(scaled_sk,0 ,copy=False)
        # np.savetxt("opencl_test/gpu_scaled.txt", scaled_np, fmt="%1.9f")
        #
        # np.savetxt("opencl_test/cpu_scaled.txt", scaled_sk, fmt="%1.9f")
        graph_np = np.empty(size, dtype=np.uint8)
        print graph_np.nbytes/1073741824.0, "GB"
        graph_g = cl.Buffer(self.ctx, mf.WRITE_ONLY, graph_np.nbytes) # allocate bytes on gpu
        print "points =", np.uint32(shape[0]), "features=", np.uint32(len(data[0])), "eps=", np.float32(self.eps)
        start = time.time()
        self.graph_kernel.makeGraph(self.queue, data.shape, None,
                                  data_g_cla.data,
                                  graph_g,
                                  np.uint32(shape[0]),
                                  np.float32(self.eps),
                                  wait_for=[scale_event])

        cl.enqueue_copy(self.queue, graph_np, graph_g)
        # cl.enqueue_copy(self.queue, distances_np, distances_g)
        print "made connection matrix, finished and copied in {} seconds".format(time.time()-start)
        return graph_np.reshape((shape[0], shape[0])) # distances_np.reshape((shape[0], shape[0])) #

    def fit(self, values):
        pass
    def gpubfs(self, graph, fa, xa):
        mf  = cl.mem_flags
        dims = graph.shape()


def check_graph(graph):
    return graph.diagonal().all()

if __name__ == "__main__":
    import cluster
    import os
    import matplotlib.pyplot as plt

    os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
    input_data = cluster.getData()[0]
    # scale(input_data, copy=False)
    # np.savetxt("opencl_test/scaled_points.txt", input_data, fmt="%1.9f")

    gdbscan = GDBSCAN(0.2, 7)
    g = gdbscan.makeGraph(input_data)
    print g
    x,y = zip(*map(lambda p: (p["x"],p["y"]),g))
    plt.plot(x,y, 'o')
    plt.ylabel("Total Traffic Volume")
    plt.xlabel("Time")
    plt.show()
    #print "Is valid graph? ", check_graph(g)
    #start = time.time()
    #d = euclidean_distances(input_data, input_data)
    #print "sklearn in {} seconds".format(time.time()-start)
