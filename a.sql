CREATE TABLE textcomments (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	parent_id INT NOT NULL,
    lft INT NOT NULL DEFAULT '0',
    rgt INT NOT NULL DEFAULT '0',
	username VARCHAR(50) NOT NULL,
	text VARCHAR(300) NOT NULL,
	post_id INT NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);