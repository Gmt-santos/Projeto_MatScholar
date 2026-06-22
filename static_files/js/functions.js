var size_screen=window.innerWidth;
// Função para deixar o header mais transparente--> Depende do tamanho da tela --> Site inteiro
window.addEventListener('scroll',()=>{
    const header_div=document.getElementsByClassName("header_div")[0];
  
    if(size_screen>1000){

        if(window.scrollY>90){

        header_div.classList.add('solid_header_background');
       

        }
        else{

            header_div.classList.remove('solid_header_background');
           

        }


    }//Continuar quando for fazer a responsividade;
    
})

// Função para mostrar a senha do usuário --> LOGIN
function toggle_visibility(){
    const checkbox_password=window.document.getElementById("show_password");
    const password_field=window.document.getElementById("password");
    if(checkbox_password.checked){
        password_field.type="text";
    }else{
        password_field.type="password";
    }

}
// Funções para alterar a visibilidade dos formulários no dashboard
// 1-> Para queries pelo nome da aula
// 2-> Para queries pelo nome do professor --> Apenas para 'Princ' users
function toggle_query_classname_visibility(){
    const forms_class_name=window.document.getElementById("form_class_name");
    forms_class_name.classList.toggle("fechado");
}
function toggle_query_professorname_visibility(){
    const forms_class_name=window.document.getElementById("form_professor_name");
    forms_class_name.classList.toggle("fechado");
}

function toggle_form_add_students_visibility(){
    const forms_class_name=window.document.getElementById("form_add_students");
    forms_class_name.classList.toggle("fechado");
}
function toggle_form_remove_students_visibility(){
    const forms_class_name=window.document.getElementById("form_remove_students");
    forms_class_name.classList.toggle("fechado");
}
function toggle_form_view_students_visibility(){
    const forms_class_name=window.document.getElementById("form_view_students");
    forms_class_name.classList.toggle("fechado");
}
function toggle_form_delete_class_visibility(){
    const forms_class_name=window.document.getElementById("form_delete_class");
    forms_class_name.classList.toggle("fechado");
}

