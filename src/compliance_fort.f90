module compliance_fort
    use iso_c_binding
    implicit none
    
    ! C-compatible message structure
    type, bind(C) :: CMessage
        integer(C_INT) :: id
        integer(C_INT) :: data
        integer(C_INT) :: proof_r
        integer(C_INT) :: proof_s
        integer(C_INT) :: public_key
    end type CMessage
    
    ! Internal Fortran message type
    type :: Message
        integer :: id
        integer :: data
        integer :: proof_r
        integer :: proof_s
        integer :: public_key
    end type Message
    
    ! Cryptographic constants
    integer, parameter :: PRIME = 23  ! взял маленькое для тестов, потом поменяем
    integer, parameter :: GENERATOR = 5  ! это работает, не трогай
    
    private :: Message, mod_pow, create_message_internal, verify_proof_internal
    
contains

    ! Convert C message to Fortran message
    function c_to_fortran(c_msg) result(f_msg)
        type(CMessage), intent(in) :: c_msg
        type(Message) :: f_msg
        
        ! просто копируем поля, ничего сложного
        f_msg%id = c_msg%id
        f_msg%data = c_msg%data
        f_msg%proof_r = c_msg%proof_r
        f_msg%proof_s = c_msg%proof_s
        f_msg%public_key = c_msg%public_key
    end function c_to_fortran
    
    ! Convert Fortran message to C message
    function fortran_to_c(f_msg) result(c_msg)
        type(Message), intent(in) :: f_msg
        type(CMessage) :: c_msg
        
        c_msg%id = f_msg%id
        c_msg%data = f_msg%data
        c_msg%proof_r = f_msg%proof_r
        c_msg%proof_s = f_msg%proof_s
        c_msg%public_key = f_msg%public_key
    end function fortran_to_c
    
    ! C-compatible function: Create ZK proof
    function create_zk_proof(id, data, secret_key, pub_key) &
            bind(C, name='create_zk_proof') result(c_msg)
        integer(C_INT), value, intent(in) :: id, data, secret_key, pub_key
        type(CMessage) :: c_msg
        type(Message) :: f_msg
        
        f_msg = create_message_internal(id, data, secret_key, pub_key)
        c_msg = fortran_to_c(f_msg)
    end function create_zk_proof
    
    ! C-compatible function: Verify ZK proof
    function verify_zk_proof(c_msg, pub_key) &
            bind(C, name='verify_zk_proof') result(is_valid)
        type(CMessage), intent(in) :: c_msg
        integer(C_INT), value, intent(in) :: pub_key
        logical(C_BOOL) :: is_valid
        type(Message) :: f_msg
        
        f_msg = c_to_fortran(c_msg)
        is_valid = verify_proof_internal(f_msg, pub_key)
    end function verify_zk_proof
    
    ! C-compatible function: Generate public key from secret
    function generate_public_key(secret_key) &
            bind(C, name='generate_public_key') result(pub_key)
        integer(C_INT), value, intent(in) :: secret_key
        integer(C_INT) :: pub_key
        
        pub_key = mod_pow(GENERATOR, secret_key, PRIME)
    end function generate_public_key
    
    ! Internal: Create message with ZK proof
    function create_message_internal(id, data, secret_key, pub_key) result(msg)
        integer, intent(in) :: id, data, secret_key, pub_key
        type(Message) :: msg
        integer :: r, k, challenge, s
        
        ! Generate random k (in production, use cryptographically secure RNG)
        ! TODO: заменить на нормальный RNG, это временно
        k = mod(id * 3 + 7, PRIME - 1) + 1  ! магия чисел, работает пока
        
        ! Compute first part of proof: r = g^k mod p
        r = mod_pow(GENERATOR, k, PRIME)
        
        ! Compute challenge (in production, use hash of r and data)
        challenge = mod(r + data, PRIME)
        
        ! Compute second part: s = k - challenge * secret_key mod (p-1)
        s = mod(k - challenge * secret_key, PRIME - 1)
        if (s < 0) s = s + (PRIME - 1)  ! фикс для отрицательных, иначе падает
        
        msg%id = id
        msg%data = data
        msg%proof_r = r
        msg%proof_s = s
        msg%public_key = pub_key
    end function create_message_internal
    
    ! Internal: Verify ZK proof
    function verify_proof_internal(msg, pub_key) result(is_valid)
        type(Message), intent(in) :: msg
        integer, intent(in) :: pub_key
        logical :: is_valid
        integer :: challenge, left_side, right_side
        
        ! Compute challenge same way as in creation
        challenge = mod(msg%proof_r + msg%data, PRIME)
        
        ! Verify: g^s * pub_key^challenge should equal r
        left_side = mod(mod_pow(GENERATOR, msg%proof_s, PRIME) * &
                        mod_pow(pub_key, challenge, PRIME), PRIME)
        right_side = msg%proof_r
        
        is_valid = (left_side == right_side)
    end function verify_proof_internal
    
    ! Fast modular exponentiation (binary exponentiation)
    function mod_pow(base, exp, modulus) result(result)
        integer, intent(in) :: base, exp, modulus
        integer :: result
        integer :: b, e, res
        
        b = mod(base, modulus)
        e = exp
        res = 1
        
        ! бинарное возведение в степень, стандартный алгоритм
        do while (e > 0)
            if (mod(e, 2) == 1) then
                res = mod(res * b, modulus)
            end if
            b = mod(b * b, modulus)
            e = e / 2  ! целочисленное деление
        end do
        
        result = res
    end function mod_pow

end module compliance_fort

