#include "blockiterator.h"

namespace bilsmtree {

BlockIterator::BlockIterator() {
  id_ = 0;
  kvs_.clear();
  iter_ = 0;
}

BlockIterator::BlockIterator(size_t id, BlockMeta bm, std::string block_data) {
  id_ = id;
  std::stringstream ss;
  size_t n;
  ss.str(block_data);
  ss >> n;
  for (size_t i = 0; i < n; ++ i) {
    std::string key_str, value_str;
    ss >> key_str >> value_str;
    kvs_.push_back(KV(key_str, value_str));
  }
  iter_ = 0;
}

BlockIterator::~BlockIterator() {
  kvs_.clear();
}

}