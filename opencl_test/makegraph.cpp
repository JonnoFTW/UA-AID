#include <iostream>
#include <fstream>
#include <math.h>

using namespace std;


void makeGraph(const float *data,
               int *graph,
               int tid,
               const int points,
               const int features,
               const float eps) {
    //int tid = get_global_id(0);
    for(size_t i = 0; i < points; i++) {
        // do the tid distances
        float sumSquares = 0;
        for(size_t j = 0; j < features; j++) {
            sumSquares += pow(data[features*tid + j] - data[features*i + j],2);
        }
        graph[i + points*tid] = sqrt(sumSquares) <= eps;
    }
}
/**
  * Check if the diagonal is all 1
  */
bool checkGraph(int* graph,int size) {
    for(size_t i =0; i < size; i++) {
        if(graph[i*size + i]!=1)
            return false;
    }
    return true;
}
int main() {
    int points =100 ;
    int features = 2;

    float data[points*features];
    int graph[points*points];
    ifstream infile("scaled_points.txt");
    {
        float x,y;
        size_t i=0;
        while(infile >> x >> y) {
            cout << x << "," << y<<" " << i <<endl;
            data[i++] = x;
            data[i++] = y;
        }
    }
    cout << "Features="<< features << endl;
    cout << "Points=" << points << endl;
    for(size_t i =0; i < points; i++) {
        makeGraph(data,graph,i,points,features,0.2f);
    }
    cout << "Valid graph? " << checkGraph(graph,points) << endl;
    ofstream out("cpp_graph.txt");
    for(size_t i= 0; i < points; i++) {
        for(size_t j= 0; j < points; j++) {
            out << graph[i*points + j] << " ";
        }
        out << endl;
    }
    out.close();
    return 0;
}