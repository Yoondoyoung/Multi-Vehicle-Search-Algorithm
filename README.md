### API Testing

#### Basic Health Check
```bash
curl https://multi-vehicle-search-algorithm.onrender.com/
```

#### Search for Single Vehicle
```bash
curl -X POST "https://multi-vehicle-search-algorithm.onrender.com/search" \
  -H "Content-Type: application/json" \
  -d '[{"length": 10, "quantity": 1}]'
```

#### Search for Multiple Vehicles
```bash
curl -X POST "https://multi-vehicle-search-algorithm.onrender.com/search" \
  -H "Content-Type: application/json" \
  -d '[
    {"length": 10, "quantity": 1},
    {"length": 20, "quantity": 2},
    {"length": 25, "quantity": 1}
  ]'
```

#### Pretty Print Results (with jq)
```bash
curl -X POST "https://multi-vehicle-search-algorithm.onrender.com/search" \
  -H "Content-Type: application/json" \
  -d '[{"length": 10, "quantity": 1}]' | jq
```