import streamlit as st     #The package that we can build the Webapps with
import functions

todos = functions.get_todos()
def add_todo():
    todo = st.session_state["new_todo"] + "\n"
    todos.append(todo)
    functions.write_todos(todos)
    print(todo)

todos = functions.get_todos()
st.title("My Todo App")
st.subheader("This is my todo app")
st.write("This app is to increase your productivity")
for index, todo in enumerate(todos):
    checkbox = st.checkbox(todo, key=todo)
    if checkbox:
        todos.pop(index)
        functions.write_todos(todos)
        del st.session_state[todo]
        st.experimental_rerun()
        print(checkbox)
st.text_input(label="Here she goes!", placeholder="Add new todo...",
              on_change=add_todo, key='new_todo')
print("Hello the app is working!")
st.session_state





