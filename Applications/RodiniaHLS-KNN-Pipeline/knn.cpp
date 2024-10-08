#include "knn.h"
extern "C"{
void load (int load_idx, float* searchSpace, float* local_searchSpace)
{
	int start_idx = load_idx * NUM_PT_IN_BUFFER * NUM_FEATURE;
L1:	for (int i(0); i < NUM_PT_IN_BUFFER*NUM_FEATURE; ++i){
		local_searchSpace[i] = searchSpace[start_idx+i];
	}
}

void compute_dist (float* local_inputQuery, float* local_searchSpace, float* local_distance)
{
    float sum;
	float feature_delta;
L2:	for (int i = 0; i < NUM_PT_IN_BUFFER; ++i) {
        sum = 0.0;
L3:		for (int j = 0; j < NUM_FEATURE; ++j){
			feature_delta = local_searchSpace[i*NUM_FEATURE+j] - local_inputQuery[j];
			sum += feature_delta*feature_delta;
		}
        local_distance[i] = sum;
	}	
}

void store (int store_idx, float* local_distance, float* distance)
{
	int start_idx = store_idx * NUM_PT_IN_BUFFER;
L4:	for (int i(0); i < NUM_PT_IN_BUFFER; ++i){
        distance[start_idx+i] = local_distance[i];
	}        
}

void workload(
	float inputQuery[NUM_FEATURE],
	float searchSpace[NUM_PT_IN_SEARCHSPACE*NUM_FEATURE],
    float distance[NUM_PT_IN_SEARCHSPACE]
){

L5:	float local_inputQuery[NUM_FEATURE];
L6:	float local_searchSpace[NUM_PT_IN_BUFFER*NUM_FEATURE];
L7:	float local_distance[NUM_PT_IN_BUFFER];

L8:	for (int i(0); i<NUM_FEATURE; ++i){
		local_inputQuery[i] = inputQuery[i];
    }
	
L9:	for (int tile_idx(0); tile_idx<NUM_TILES; ++tile_idx){
		load(tile_idx, searchSpace, local_searchSpace);
		compute_dist(local_inputQuery, local_searchSpace, local_distance);
        store(tile_idx, local_distance, distance);
	}

	return;
}
}
