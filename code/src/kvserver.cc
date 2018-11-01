#include "kvserver.h"

KVServer::KVServer() {
  lsmtree_ = new LSMTree();
  logmanager_ = new LogManager();
}

KVServer::~KVServer() {
  delete lsmtree_;
  delete logmanager_;
}

Slice KVServer::Get(const Slice& key) {
  Slice location_ = lsmtree_->Get(key);
  Slice value_ = logmanager_->Get(location);
  return value_;
}

void MinorCompact(const SkipList* sl) {
  std::vector<KV> data_ = sl->GetAll();
  // TODO: RESIZE BEFORE PUSH_BACK
  std::vector<KV> kvs_;
  for (int i = 0; i < data_.size(); ++ i) {
    KV kv_ = data_[i];
    Slice location_ = logmanager_->Append(kv_);
    kvs_.push_back(KV(kv_.key_, location_))
  }
  Table* table_ = new Table(kvs_);
  lsmtree_->AddTableToL0(table_);
}