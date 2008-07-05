'''
 it looks like you need to have the Entity Model declared in
 order to GAE to query, otherwise the system raises a KindError

 this file is where you enter an array with all files containing the
 db.Model and db.Expando classes that you want to expose in the 
 REST API they will all be imported
 
 Example:
 models = ['file.py', 'dir/mymodels.py' ]
'''
models = []