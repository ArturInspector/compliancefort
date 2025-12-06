! ============================================================
! Математическая очередь с ZK-верификацией
! Демонстрация возможностей Fortran в криптографии
! ============================================================
!
! Что это делает:
! - Создает очередь сообщений (как Kafka, но проще)
! - Каждое сообщение имеет ZK-доказательство (Schnorr протокол)
! - Можно проверить, что сообщение валидно, не раскрывая его содержимое
!
! Математика: используем простой протокол Schnorr для доказательства
! знания секретного ключа без его раскрытия

program zk_queue
    use compliance_fort
    implicit none
    
    type :: Queue
        type(Message), allocatable :: messages(:)
        integer :: size            ! Текущий размер очереди
        integer :: capacity        ! Максимальная вместимость
    end type Queue
    
    ! Константы для очереди
    integer, parameter :: MAX_QUEUE = 100   ! Максимальный размер очереди
    
    ! Переменные
    type(Queue) :: message_queue
    integer :: i, secret_key, public_key
    type(Message) :: msg
    
    ! Инициализация очереди
    call init_queue(message_queue, MAX_QUEUE)
    
    print *, '========================================'
    print *, 'Математическая очередь с ZK-верификацией'
    print *, '========================================'
    print *, ''
    
    ! Генерируем секретный ключ (в реальности это должно быть случайным)
    secret_key = 7  ! хардкод для демки, потом убрать
    public_key = generate_public_key_fortran(secret_key)
    
    print *, 'Секретный ключ (известен только отправителю):', secret_key
    print *, 'Публичный ключ (все знают):', public_key
    print *, ''
    
    ! Добавляем несколько сообщений в очередь
    do i = 1, 5
        msg = create_message(i, i * 10, secret_key, public_key)
        call enqueue(message_queue, msg)
        print *, 'Добавлено сообщение #', i, ' с данными:', i * 10
    end do
    
    print *, ''
    print *, 'Текущий размер очереди:', message_queue%size
    print *, ''
    
    ! Проверяем ZK-доказательства для всех сообщений
    print *, 'Проверка ZK-доказательств:'
    print *, '----------------------------------------'
    do i = 1, message_queue%size
        if (verify_proof(message_queue%messages(i), public_key)) then
            print *, 'Сообщение #', message_queue%messages(i)%id, &
                     ' - доказательство ВАЛИДНО ✓'
        else
            print *, 'Сообщение #', message_queue%messages(i)%id, &
                     ' - доказательство НЕВАЛИДНО ✗'
        end if
    end do
    
    print *, ''
    print *, 'Обработка очереди (как в Kafka):'
    print *, '----------------------------------------'
    
    ! Обрабатываем очередь (извлекаем сообщения)
    do while (message_queue%size > 0)
        msg = dequeue(message_queue)
        print *, 'Обработано сообщение #', msg%id, &
                 ' с данными:', msg%data
    end do
    
    print *, ''
    print *, 'Очередь пуста. Все сообщения обработаны!'
    
contains

    ! Инициализация очереди
    subroutine init_queue(q, cap)
        type(Queue), intent(out) :: q
        integer, intent(in) :: cap
        
        allocate(q%messages(cap))
        q%size = 0
        q%capacity = cap
    end subroutine init_queue
    
    ! Добавление сообщения в очередь
    subroutine enqueue(q, msg)
        type(Queue), intent(inout) :: q
        type(Message), intent(in) :: msg
        
        if (q%size >= q%capacity) then
            print *, 'ОШИБКА: Очередь переполнена!'
            return  ! просто выходим, можно было бы расширить массив
        end if
        
        q%size = q%size + 1
        q%messages(q%size) = msg
    end subroutine enqueue
    
    ! Извлечение сообщения из очереди
    function dequeue(q) result(msg)
        type(Queue), intent(inout) :: q
        type(Message) :: msg
        integer :: i
        
        if (q%size == 0) then
            print *, 'ОШИБКА: Очередь пуста!'
            return
        end if
        
        ! Берем первое сообщение (FIFO - First In First Out)
        msg = q%messages(1)
        
        ! Сдвигаем все сообщения влево
        ! неэффективно для больших очередей, но работает
        do i = 1, q%size - 1
            q%messages(i) = q%messages(i + 1)
        end do
        
        q%size = q%size - 1
    end function dequeue
    

end program zk_queue

