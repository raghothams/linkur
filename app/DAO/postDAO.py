
import conf
import psycopg2
import hashlib
import random
import string

from app.model.user import User
from app.model.post import Post


class PostDAO:

    def __init__(self):

        # Connect to db
        self.db = psycopg2.connect(
                                    database=conf.PG_DB,
                                    host=conf.PG_HOST,
                                    port=conf.PG_PORT,
                                    user=conf.PG_USER,
                                    password=conf.PG_PASSWORD
                                )


    # get posts for a group 
    def get_posts_for_group(self, group_id, user_id):

        cur = None
        result = None

        try:
            # Get the db cursor & execute the Select query
            cur = self.db.cursor();

            cur.execute("SELECT * FROM public.vw_user_posts WHERE \
                            group_id = %s AND user_id = %s", (group_id, user_id))
            
            rows = cur.fetchall()
            posts = []

            for row in rows:
                post = Post()
                post.id = row[0]
                post.title = row[1]
                post.link = row[2]
                post.group = row[3]
                post.added_by = row[4]
                post.date = row[5]
                post.tags = row[6]

                posts.append(post.serialize())

            
            result = posts

        except Exception as e:

            print "Error occured reading posts"
            print e
            raise e
            
        finally:
        
            cur.close()
            return result


    # Get a single post
    def get(self, post_id, user_id):

        cur = None
        result = None

        try:

            cur = self.db.cursor()

            cur.execute("SELECT * FROM public.vw_user_posts WHERE \
                            id = %s AND user_id = %s", (post_id, user_id))

            row = cur.fetchone()
            post = Post()

            post.id = row[0]
            post.title = row[1]
            post.link = row[2]
            post.group = row[3]
            post.added_by = row[4]
            post.date = row[5]
            post.tags = row[6]

            result = post.serialize()

        except Exception as e:

            print "An error occured while reading post by id"
            print e
            raise e

        finally:

            cur.close()
            return result


    # Add entry in posts table
    def create(self, post):

        cur = None
        result = None

        try:

            cur = self.db.cursor()
            cur.execute("INSERT INTO public.posts \
                            (TITLE, LINK, GROUP_ID, TAGS, ADDED_BY, DATE) \
                            VALUES (%s,%s,%s,%s,%s,%s) RETURNING id, group_id",
                            (
                                post.title,
                                post.link,
                                post.group,
                                post.tags,
                                post.added_by,
                                post.date
                            ))

            if cur.rowcount == 1:
                row = cur.fetchone()
                self.db.commit()
                result = row[0]

        except Exception as e:

            print "An error occured while inserting post"
            print e

            self.db.rollback()
            raise e
        
        finally:

            cur.close()
            return result


    # Delete entry from posts table 
    def delete(self, post_id, user_id):

        cur = None
        result = None
        post = None

        try:
            post = self.get(post_id, user_id)
            cur = self.db.cursor()
            cur.execute("DELETE FROM public.posts WHERE id = %s AND \
                    group_id IN (SELECT group_id FROM public.user_groups \
                    WHERE user_id = %s)", (post_id, user_id))

            if cur.rowcount == 1:
                result = True
                self.db.commit()

        except Exception as e:

            print "An error occurred while deleting post"
            print e

            self.db.rollback()
            raise e
        
        finally:
            
            cur.close()
            return result
    

    # Update entry in posts table
    def update(self, post, user_id):

        cur = None
        result = None

        try:

            cur = self.db.cursor()
            cur.execute("UPDATE public.posts SET title=%s, link=%s, group_id=%s,\
                    tags=%s WHERE id=%s AND id IN ( SELECT post_id AS id FROM \
                    public.user_reading_list WHERE post_id=%s AND user_id=%s )",
                    (
                        post.title,
                        post.link,
                        post.group,
                        post.tags,
                        post.id,
                        post.id,
                        user_id,
                    ))

            if cur.rowcount == 1:
                result = True
                self.db.commit()

        except Exception as e:

            print "An error occured while updating post"
            print e

            self.db.rollback()
            raise e

        finally:

            cur.close()
            return result

    
    # Add entry into user_posts table
    def associate_user(self, postid, groupid):

        cur = None
        result = None

        try:

            cur = self.db.cursor()
            
            #get all user for the group
            cur.execute("SELECT user_id FROM public.user_groups WHERE \
                               group_id = %s", (groupid,))
            rows = cur.fetchall()

            #create user post association for all the users in the group
            cur.executemany("INSERT INTO public.user_reading_list \
                            (user_id, post_id) VALUES (%s,%s)", \
                            [ (row[0], postid) for row in rows])

            if cur.rowcount > 0:
                self.db.commit()
                result = True
        
        except Exception as e:

            print "Error while creating user post association"
            print e
            self.db.rollback()
            raise e
            
        finally:

            cur.close()
            return result

    
    # Delete entry from user_posts table
    def remove_user_association(self, postid, userid):

        cur = None
        result = None

        try:

            cur = self.db.cursor()

            cur.execute("DELETE FROM public.user_reading_list WHERE \
                            user_id = %s AND post_id = %s",
                            (userid, postid))

            if cur.rowcount > 0:
                result = True
                self.db.commit()

        except Exception as e:

            print "Error removing user post association"
            print e
            self.db.rollback()
            raise e

        finally:
            
            cur.close()
            return result
    

    # archive post
    def archive(self, postid, userid):

        cur = None
        result = None

        try:

            cur = self.db.cursor()

            cur.execute("INSERT INTO public.user_archived_posts (user_id, post_id) VALUES (%s, %s)",
                            (userid, postid))

            if cur.rowcount > 0:
                result = True
                self.db.commit()

        except Exception as e:

            print "Error archiving post"
            print e
            self.db.rollback()
            raise e

        finally:
            
            cur.close()
            return result

    def __del__(self):

        self.db.close()

