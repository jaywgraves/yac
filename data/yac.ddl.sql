drop table if exists author;
create table author(
    id integer primary key,
    name text,
    last_name text,
    host text,
    room text,
    bio text,
    choice_count_1 int default 0,
    choice_count_2 int default 0,
    choice_count_3 int default 0,
    choice_count_4 int default 0,
    choice_count_5 int default 0,
    sess_1_cnt int default 0,
    sess_1_high_cnt int default 0,
    sess_1_err boolean,
    sess_2_cnt int default 0,
    sess_2_high_cnt int default 0,
    sess_2_err boolean
);

drop table if exists student;
create table student(
    id integer primary key autoincrement,
    name text,
    teacher text,
    grade text,
    choice_1 integer,
    choice_2 integer,
    choice_3 integer,
    choice_4 integer,
    choice_5 integer,
    complete text default "N",
    score numeric,
    error text default "N",
    sess_1 int default 0 not null,
    sess_1_lock text default "N",
    sess_2 int default 0 not null,
    sess_2_lock text default "N",
    note text
);

--drop trigger if exists student_complete;
--create trigger student_complete after UPDATE of sess_1,sess_2 on student 
--when new.sess_1 <> 0 and new.sess_2 <> 0
--begin
--    update student set complete = 'Y' where id = old.id;
--end;

drop table if exists changes;
create table changes(
    id integer primary key autoincrement,
    s_id int,
    sess int,
    prev int,
    new int
);



drop table if exists teacher;
create table teacher(
    name text primary key
);
