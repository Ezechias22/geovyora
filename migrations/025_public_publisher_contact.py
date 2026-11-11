"""Publish the contact details explicitly supplied by the site owner."""


def apply(connection, sql):
    for key, value in [('contact_person', 'Ezechias Toussaint'),
                       ('contact_email', 'contact@haytiles.com')]:
        connection.execute(sql('INSERT INTO settings(key,value) VALUES (?,?) '
                               'ON CONFLICT(key) DO UPDATE SET value=excluded.value'), (key, value))
    connection.execute(sql("INSERT INTO settings(key,value) VALUES ('contact_company','Haytiles') "
                           "ON CONFLICT(key) DO NOTHING"))
    connection.execute(sql("UPDATE settings SET value='Haytiles' WHERE key='contact_company' AND value=''"))
