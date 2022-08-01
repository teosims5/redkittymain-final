INSERT INTO user (username, email, password)
VALUES 
    ('test1', 'test1@example.com', '$5$rounds=535000$xa4hyV8oBfEY8efA$stRZLXqufA/UG1uI1/QVDSV3CZvkH1g00lhpN6HKAo/'),
    ('test2', 'test2@example.com','$5$rounds=535000$xa4hyV8oBfEY8efA$stRZLXqufA/UG1uI1/QVDSV3CZvkH1g00lhpN6HKAo/');
INSERT INTO post (title, bookTitle, photo, body,author, create_date)
VALUES 
    ('test title 1', 'test bookTitle 1', 'https://dummyimage.com/150', 'it is in the time of life that things should be followed', 1, '2019-01-01 00:00:00');