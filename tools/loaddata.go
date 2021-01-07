package main

import (
	"context"
	"fmt"
	redisbloom "github.com/RedisBloom/redisbloom-go"
	"github.com/go-redis/redis/v8"
	"time"
)

var ctx = context.Background()

func main() {
	var client = redisbloom.NewClient("localhost:6379", "nohelp", nil)
	rdb := redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
	})
	start := time.Now()
	for w := 0; w < 1000000; w++ {
		item := fmt.Sprintf("0123456789-%06d", w)
		client.Add("MY-BLOOM", item)
		rdb.SAdd(ctx, "MY-SET", item)
	}
	elapsed := time.Since(start)
	fmt.Println("Load took:", elapsed)

}
