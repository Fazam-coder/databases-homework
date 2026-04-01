# 1 задание
* Seq Scan
* Никакие индексы не помогают, т.к. они не используются в WHERE 
* CREATE INDEX idx_exam_events_user_id ON exam_events(user_id, created_at)
* Теперь в плане используется индекс

# 2 задание
* Nested Loop с индексами 
* Потому что есть индекс на сreated_at, но таблицы не отсортированы 
* Индекс на сreated_at полезен 
* Создать индекс на exam_users(country) using hash, чтобы использовался hash join

# 5 задание
```sql
create table name(
    -- все поля таблицы
) partition by range(log_date)

create table v1 partition of name for values('январь 2025')
```
