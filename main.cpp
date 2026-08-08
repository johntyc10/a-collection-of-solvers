#include <iostream>
#include <array>
#include <vector>
#include <algorithm>
#include <cmath>
#include <climits>
#include <fstream>
#include <sstream>
#include <chrono>
using namespace std;
using Tile = u_int8_t;


struct MoveList {
    int pos[4];
    char dir[4];
    int size = 0;

    void add(int p, char d) {
        pos[size] = p;
        dir[size] = d;
        ++size;
    }
};


class FifteenPuzzleSolver {
    int height;
    int width;
    vector<Tile> board;

    // log variables
    int _maxDepth = 0;
    long long _evaluatedNodes = 0;

    public:
        FifteenPuzzleSolver(int r, int c, vector<Tile> _board) {
            height = r;
            width = c;
            board = _board;
        };

        vector<pair<Tile, char>> solve() {
            if (!isBoardSolvable()) {
                cout << "Board is NOT solvable. Check your input and try again." << endl;
                exit(0);
            }

            int initManhattanDistance = 0;
            for (int i = 0; i < board.size(); i++) {
                Tile tile = board[i];
                if (tile == 0)
                    continue;
                int tileRow = i / width;
                int tileColumn = i % width;
                initManhattanDistance += abs(tileRow - goalRow(tile)) + abs(tileColumn - goalColumn(tile));
            }

            int t = initManhattanDistance; // + linearConflictCount(board) * 2;

            int blankIdx = findBlankIdx(board);
            vector<pair<Tile, char>> path;
            while (t != -1) {
                t = search(board, 0, t, path, '0', blankIdx, initManhattanDistance);
            }
            return path;
        }

        long long getEvaluatedNodeCount() {
            return _evaluatedNodes;
        }

    private:
        int search(vector<Tile>& board, int depth, int threshold, vector<pair<Tile, char>>& path, char lastDir, int blankIdx, int lastManhattanDistance) {
            int h = lastManhattanDistance; // + linearConflictCount(board) * 2;
            int f = depth + h;
            if (f > threshold) {
                return f;
            }

            if (h == 0) {
                return -1;
            }

            if (depth > _maxDepth)
                _maxDepth = depth;

            int min_f = INT_MAX;
            MoveList ml = possibleNextMoves(blankIdx);
            for (int i = 0; i < ml.size; i++) {
                int moveTileIdx = ml.pos[i];
                char dir = ml.dir[i];
                if (lastDir != '0' && dir == oppositeDir(lastDir))
                    continue;

                _evaluatedNodes++;
                if (_evaluatedNodes % 10000000 == 0) {
                    cout << "----------------------" << endl;
                    cout << "Gone through " << _evaluatedNodes << " nodes, max depth = " << _maxDepth << endl;
                }

                // calculate new manhattan distance
                Tile moveTile = board[moveTileIdx];

                int moveTileRow = moveTileIdx / width;
                int moveTileColumn = moveTileIdx % width;
                int newBlankRow = blankIdx / width;
                int newBlankColumn = blankIdx % width;

                int oldContrib = abs(moveTileRow - goalRow(moveTile)) + abs(moveTileColumn - goalColumn(moveTile));
                int newContrib = abs(newBlankRow - goalRow(moveTile)) + abs(newBlankColumn - goalColumn(moveTile));

                int manhattanDistance = lastManhattanDistance - oldContrib + newContrib;

                // apply move
                swap(board[moveTileIdx], board[blankIdx]);
                path.push_back(make_pair(moveTile, dir));

                int f = search(board, depth + 1, threshold, path, dir, moveTileIdx, manhattanDistance);
                if (f == -1) {
                    return -1;
                }
                if (f < min_f)
                    min_f = f;

                // undo
                path.pop_back();
                swap(board[moveTileIdx], board[blankIdx]);
            }

            return min_f;
        }

        char oppositeDir(char dir) {
            // cout << dir << endl;
            if (dir == 'L') return 'R';
            if (dir == 'R') return 'L';
            if (dir == 'U') return 'D';
            if (dir == 'D') return 'U';
        }

        // O(n^2) naive algorithm because arr size is small
        int countInversions(vector<Tile>& arr) {
            int count = 0;
            for (int i = 0; i < arr.size() - 1; i++) {
                for (int j = i + 1; j < arr.size(); j++) {
                    count += arr[i] > arr[j];
                }
            }
            return count;
        };

        int findBlankIdx(vector<Tile>& board) {
            auto it = find(board.begin(), board.end(), 0);
            return distance(board.begin(), it);
        }

        bool isBoardSolvable() {
            vector<Tile> boardWithoutBlank = board;
            erase(boardWithoutBlank, 0);
            int inversionCount = countInversions(boardWithoutBlank);

            if (width % 2 == 1) {
                return inversionCount % 2 == 0;
            }

            int blankIndex = findBlankIdx(board);
            int blankRowFromBottom = height - blankIndex / width;

            return (inversionCount + blankRowFromBottom) % 2 == 1;
        }

        vector<Tile> getDefaultSolution() {
            vector<Tile> defaultSolution(height * width);
            for (int i = 1; i <= height * width; i++) {
                defaultSolution[i] = i % (height * width);
            }
            return defaultSolution;
        }

        int goalIdx(Tile tile) {
            return (tile - 1) % (height * width);
        }

        int goalRow(Tile tile) {
            // row starts from 0
            if (tile == 0)
                return height - 1;
            return (tile - 1) / width;
        }

        int goalColumn(Tile tile) {
            // column starts from 0
            if (tile == 0)
                return width - 1;
            return (tile - 1) % width;
        }

        int linearConflictCount(vector<Tile>& board) {
            int conflicts = 0;

            // rows
            for (int i = 0; i < height; i++) {
                for (int c1 = 0; c1 < width; c1++) {
                    Tile t1 = board[width * i + c1];
                    if (t1 == 0 || goalRow(t1) != i)
                        continue;
                    for (int c2 = c1 + 1; c2 < width; c2++) {
                        Tile t2 = board[width * i + c2];
                        if (t2 == 0 || goalRow(t2) != i)
                            continue;
                        // both belong to this row; check order
                        if (goalIdx(t1) > goalIdx(t2))
                            conflicts++;
                    }
                }
            }

            // columns
            for (int j = 0; j < width; j++) {
                for (int r1 = 0; r1 < height; r1++) {
                    Tile t1 = board[j + r1 * width];
                    if (t1 == 0 || goalColumn(t1) != j)
                        continue;
                    for (int r2 = r1 + 1; r2 < height; r2++) {
                        Tile t2 = board[j + r2 * width];
                        if (t2 == 0 || goalColumn(t2) != j)
                            continue;
                        if (goalIdx(t1) > goalIdx(t2))
                            conflicts++;
                    }
                }
            }

            return conflicts;
        }

        MoveList possibleNextMoves(int blank) {
            MoveList ml;
            int r = blank / width;
            int c = blank % width;

            if (c < width - 1)
                ml.add(blank + 1, 'L'); // tile to the right moves Left
            if (c > 0)
                ml.add(blank - 1, 'R'); // tile to the left moves Right
            if (r < height - 1)
                ml.add(blank + width, 'U'); // tile below moves Up
            if (r > 0)
                ml.add(blank - width, 'D'); // tile above moves Down

            return ml;
        }

        int getBlankIdxByMove(int moveTileIdx, char dir) {
            if (dir == 'L')
                return moveTileIdx - 1;
            if (dir == 'R')
                return moveTileIdx + 1;
            if (dir == 'U')
                return moveTileIdx - width;
            if (dir == 'D')
                return moveTileIdx + width;
        }

        void applyMove(vector<Tile>& board, int moveTileIdx, char dir) {
            swap(board[moveTileIdx], board[getBlankIdxByMove(moveTileIdx, dir)]);
        }

        // apply and undo swaps the same two tiles
        inline void undoMove(vector<Tile>& board, int moveTileIdx, char dir) {
            applyMove(board, moveTileIdx, dir);
        }
};


long long time_now_ns() {
    // Get the current time point
    auto now = std::chrono::system_clock::now();

    // Get duration since epoch
    auto duration = now.time_since_epoch();

    // Cast duration explicitly to nanoseconds
    auto nanoseconds = std::chrono::duration_cast<std::chrono::nanoseconds>(duration);

    // Extract the raw 64-bit integer value
    return nanoseconds.count();
}


int main() {
    // vector<Tile> board = {1, 5, 7, 2, 8, 6, 0, 3, 4};
    ifstream fin("input.txt");
    if (!fin) {
        cerr << "Cannot open input.txt" << endl;
        return 1;
    }

    int height, width;
    fin >> height >> width;

    vector<Tile> board;
    board.reserve(height * width);

    for (int i = 0; i < height * width; i++) {
        int x;
        fin >> x;
        board.push_back(static_cast<Tile>(x));
    }
    fin.close();

    // optional sanity check
    if (board.size() != static_cast<size_t>(height * width)) {
        cerr << "Board size mismatch" << endl;
        return 1;
    }

    long long timestamp_ns = time_now_ns();

    FifteenPuzzleSolver solver(height, width, board);
    vector<pair<Tile, char>> solution = solver.solve();

    long long duration_ns = time_now_ns() - timestamp_ns;
    cout << "Solving the board took " << duration_ns << " nanoseconds. (" << (double)duration_ns * 1e-9 << " seconds)" << endl;
    cout << "The solver had gone through " << solver.getEvaluatedNodeCount() << " nodes." << endl;

    cout << "The solution is:" << endl;
    for (int i = 0; i < solution.size(); i++) {
        cout << +solution[i].first << " " << solution[i].second << endl;
        if ((i + 1) % 5 == 0 && (i + 1) != solution.size()) {
            cout << "Press enter to display the next five steps (" << i + 1 << "/" << solution.size() << " displayed): ";
            cin.ignore(std::numeric_limits<streamsize>::max(), '\n');
        }
    }
}
