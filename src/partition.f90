module partition_fort
    use compliance_fort 
    implicit none

    ! one partition structure
    type :: Partition
        type(Message), allocatable :: messages(:)
        integer :: size
        integer :: capacity
        integer :: partition_id
    end Type Partition

    type :: PartitionManager
        type(partition), allocatable :: partitions(:) ! array
        integer :: num_partitions
    end type PartitionManager

    public :: partition, PartitionManager
    public :: init_partition_manager, add_message_to_partition
    public :: hash_key, get_partition_id

contains

    ! polynomic hash function
    function hash_key(key, num_partitions) result(partition_id)
        integer, intent(in) :: key, num_partitions
        integer :: partition_id
        integer, parameter :: HASH_A = 7 ! 1 hash const
        integer, parameter :: HASH_B = 13 ! 1 hash const
        
        ! formula (key * a + b) mod num_partitions